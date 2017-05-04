import os
import codecs
from django.core.management.base import BaseCommand
from django.conf import settings

from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.rl_config import defaultPageSize

PAGE_WIDTH  = defaultPageSize[0]
PAGE_HEIGHT = defaultPageSize[1]

from core.models import Person


class Command(BaseCommand):
    help = "Create certificates for persons."
    requires_system_checks = True
    requires_migrations_checks = True

    def handle(self, *args, **options):

        for person in Person.objects.all():

            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            name = "{} {}".format(str(person.first_name), str(person.last_name))

            text_width = stringWidth(name)
            y = 1050

            pdf_text_object = canvas.beginText((PAGE_WIDTH - text_width) / 2.0, y)
            pdf_text_object.textOut(name)

            can.drawString(10, 100, name)
            can.save()

            packet.seek(0)
            new_pdf = PdfFileReader(packet)
            existing_pdf = PdfFileReader(open(os.path.join(settings.MEDIA_ROOT, "certificate.pdf"), "rb"))
            output = PdfFileWriter()


            page = existing_pdf.getPage(0)
            page.mergePage(new_pdf.getPage(0))
            output.addPage(page)

            outputStream = open(os.path.join(settings.MEDIA_ROOT, "diplomas", str(person.id) + "-" + "diploma.pdf"), "wb")
            output.write(outputStream)
            outputStream.close()
