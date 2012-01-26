import os
import xlrd

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from olcc.models import Product

class Command(BaseCommand):
    """
    This command parses an Excel spreadsheet containing OLCC product
    and price data and imports it into the database.

    A typical price list can be found here: http://www.olcc.state.or.us/pdfs/Numeric_Price_List_Next_Month.xls
    """
    args = "<filename>"
    help = "Parses an excel document of OLCC price data."

    option_list = BaseCommand.option_list + (
        make_option('--quiet', action='store_true', dest='quiet', default=False,
            help='Suppress all output except errors'),
    )

    def handle(self, *args, **options):
        quiet = options.get('quiet', False)

        # Get our filename
        try:
            filename = args[0]
            if not os.path.exists(filename):
                raise CommandError("The file %s does not exist!" % filename)
        except IndexError:
            raise CommandError("You must specify a filename!")

        if not quiet:
            self.stdout.write("Importing prices from %s\n" % filename)
            self.stdout.flush()

        # Import workbook
        wb = xlrd.open_workbook(filename)

        # Get the first sheet
        sheet = wb.sheet_by_index(0)

        # Loop over worksheet
        count = 0
        for rownum in range(sheet.nrows):
            # Get the row
            values = sheet.row_values(rownum)
            if len(values) > 0:
                # Make sure the first column contains a valid product code
                if values[0] and values[0][0].isdigit():
                    if not quiet:
                        self.stdout.write(str(values))
                        self.stdout.write("\n")
                        self.stdout.flush()

                    # Import the product and price data
                    Product.from_row(values)
                    count += 1

        if not quiet:
            self.stdout.write("\nImported %d rows of price data\n" % count)
