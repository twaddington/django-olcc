import os
import xlrd

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from olcc.models import Product

class Command(BaseCommand):
    """
    This command parses an Excel spreadsheet containing OLCC product
    and price data and imports it into the database.

    :todo: Determine spreadsheet type?
    :todo: Import store data!
    :todo: Import price data!
    :todo: Import price history data!
    :todo: Lock file?
    :todo: Tests!
    """
    args = "<filename>"
    help = "Parses an excel document of OLCC price data."

    option_list = BaseCommand.option_list + (
        make_option('--quiet', action='store_true', dest='quiet', default=False,
            help='Suppress all output except errors'),
    )

    def import_prices(self, sheet):
        """
        Import a list of price and product data from the first
        sheet in an Excel workbook.
        """
        pass

    def import_stores(self, sheet):
        """
        Import a list of store data from the first sheet
        in an Excel workbook.
        """
        pass

    def handle(self, *args, **options):
        quiet = options.get('quiet', False)

        print "hello!"
        import sys
        sys.exit()

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
