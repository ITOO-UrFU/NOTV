import os
import codecs
from django.core.management.base import BaseCommand
from django.conf import settings

from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from core.models import Person


class Command(BaseCommand):
    help = "Create certificates for persons."
    requires_system_checks = True
    requires_migrations_checks = True

    def handle(self, *args, **options):

        for person in Person.objects.all():

            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            name = "{} {}".format(str(person.first_name), str(person.last_name))
            can.drawString(10, 100, name)
            can.save()

            packet.seek(0)
            new_pdf = PdfFileReader(packet)
            existing_pdf = PdfFileReader(codecs.open(os.path.join(settings.MEDIA_ROOT, "certificate.pdf"), "rb"))
            output = PdfFileWriter()


            page = existing_pdf.getPage(0)
            page.mergePage(new_pdf.getPage(0))
            output.addPage(page)

            outputStream = open(os.path.join(settings.MEDIA_ROOT, "diplomas", str(person.id) + "-" + "diploma.pdf"), "wb")
            output.write(outputStream)
            outputStream.close()
