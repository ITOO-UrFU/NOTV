from django.core.management.base import BaseCommand

from pyPdf import PdfFileWriter, PdfFileReader
import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from core.models import Person


class Command(BaseCommand):
    help = "Create certificates for persons."
    requires_system_checks = True
    requires_migrations_checks = True

    def handle(self, *args, **options):

        for person in Person.objects.all():

            packet = StringIO.StringIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.drawString(10, 100, f"{person.first_name} {person.last_name}")
            can.save()

            packet.seek(0)
            new_pdf = PdfFileReader(packet)
            existing_pdf = PdfFileReader(open("certificate.pdf", "rb"))
            output = PdfFileWriter()


            page = existing_pdf.getPage(0)
            page.mergePage(new_pdf.getPage(0))
            output.addPage(page)

            outputStream = open(f"{person.id}-diploma.pdf", "wb")
            output.write(outputStream)
            outputStream.close()
