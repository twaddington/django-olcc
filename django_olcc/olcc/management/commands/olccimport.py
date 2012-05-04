import os
import time
import xlrd

from django.core.management.base import BaseCommand, CommandError
from geopy import geocoders
from olcc.models import Product, Store
from optparse import make_option

class Command(BaseCommand):
    """
    This command parses an Excel spreadsheet containing OLCC product
    and price data and imports it into the database.

    :todo: Import price data!
    :todo: Import price history data!
    :todo: Lock file?
    :todo: Tests!
    """
    args = "<filename>"
    help = "Parses an excel document of OLCC price data."

    option_list = BaseCommand.option_list + (
        make_option('--quiet', action='store_true', dest='quiet',
            default=False, help='Suppress all output except errors'),
        make_option('--type', choices=('prices', 'stores',), dest='type',
            default='prices', help='Suppress all output except errors'),
    )

    def uprint(self, msg):
        """
        Unbuffered print.
        """
        if not self.quiet:
            self.stdout.write("%s\n" % msg)
            self.stdout.flush()

    def import_prices(self, sheet):
        """
        Import a list of price and product data from the first
        sheet in an Excel workbook.
        """
        # ...

    def import_stores(self, sheet):
        """
        Import a list of store data from the first sheet
        in an Excel workbook.
        """
        # Get our geocoder
        g = geocoders.Google()

        for n in range(sheet.nrows):
            values = sheet.row_values(n)

            store_key = values[0]
            if isinstance(store_key, (int, long, float)):
                # Create new store instance
                store = Store.from_row(values)

                try:
                    # Geocode the store location
                    address, pos = g.geocode(store.address_raw)

                    store.address = address.strip()
                    store.latitude = pos[0]
                    store.longitude = pos[1]
                    store.save()
                except ValueError:
                    # Multiple addresses returned!
                    self.uprint("Multiple addresses returned for store %s!" % store.key)

                # Some output
                self.uprint(store)

                # Sleep to prevent hitting the geocoder rate limit
                time.sleep(.35)

    def handle(self, *args, **options):
        self.quiet = options.get('quiet', False)
        import_type = options.get('type')

        try:
            # Get our filename
            filename = args[0]

            # Some output
            self.uprint("Importing '%s' from: \n\t%s" % (import_type, filename))

            # Import workbook
            wb = xlrd.open_workbook(filename)

            # Get the first sheet
            sheet = wb.sheet_by_index(0)

            if import_type == 'stores':
                self.import_stores(sheet)
            elif import_type == 'prices':
                self.import_prices(sheet)
            else:
                raise CommandError("Cannot start import of type: '%s'" % import_type)
        except IndexError:
            raise CommandError("You must specify a filename!")
        except IOError, e:
            raise CommandError("No such file: '%s'" % e.filename)

