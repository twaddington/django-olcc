import os
import xlrd
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    """
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
            wb = xlrd.open_workbook(filename);
            self.stdout.write("Sheet Names:\n%s\n" % wb.sheet_names())

            # Get the first sheet
            sheet = wb.sheet_by_index(0)

            # Loop over worksheet
            #[u'Report Date:  ', '', 40863.0, '', '', '']
            #['', '', '', '', '', '']
            #[u'Item Code', u'Item Status', u'Description', u'Size', u'Bottles per Case', u'Bottle Price']
            #[u'0102B', u'@', u'GLENFIDDICH SNOW PHOENIX', u'750 ML', 6.0, 92.950000000000003]
            for rownum in range(sheet.nrows):
                print sheet.row_values(rownum)
        except IOError as (errno, strerror):
            raise CommandError("%s" % strerror)
        except IndexError:
            raise CommandError("You must specify a filename!")
