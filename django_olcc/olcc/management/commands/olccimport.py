import os
import xlrd

from django.core.management.base import BaseCommand, CommandError

from olcc.models import Product

class Command(BaseCommand):
    """
    :todo: Use optparse to add a --quiet option to supress all output except errors.
    :todo: Write a separate management command to fetch the latest price document.
    """
    args = "<filename>"
    help = "Parses an excel document of OLCC price data."

    def handle(self, *args, **options):
        try:
            filename = args[0]
            if not filename:
                # Get latest file and hash for update
                # ...
                pass
            self.stdout.write("Importing from \"%s\"...\n" % filename)

            # Import workbook
            wb = xlrd.open_workbook(filename)
            self.stdout.write("Sheet Names:\n%s\n" % wb.sheet_names())

            # Get the first sheet
            sheet = wb.sheet_by_index(0)

            # Loop over worksheet
            for rownum in range(sheet.nrows):
                if rownum < 3:
                    continue
                values = sheet.row_values(rownum)
                if len(values) > 0:
                    if values[0][0] and values[0][0].isdigit():
                        try:
                            # TODO: Updating products
                            Product.from_row(values)
                        except IndexError:
                            pass
        except IOError as (errno, strerror):
            raise CommandError("%s" % strerror)
        except IndexError:
            raise CommandError("You must specify a filename!")
