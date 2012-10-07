import datetime

from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction
from olcc.models import Product, ProductPrice
from optparse import make_option

class Command(BaseCommand):
    help = """\
    A command to be run periodically to calculate Product status
    from updated price data.

    This script will iterate over all product records and toggle
    the 'on_sale' property if the item's price has dropped since
    the previous month.

    This command will only execute on the first of the month. You can
    force it to execute on other days with the '--force' option."""

    option_list = BaseCommand.option_list + (
        make_option('--force', action='store_true', dest='force',
            default=False, help='Force the command to execute.'),
        make_option('--quiet', action='store_true', dest='quiet',
            default=False, help='Suppress all output except errors'),
    )

    def uprint(self, msg):
        """
        Unbuffered print.
        """
        if not self.quiet:
            self.stdout.write("%s\n" % msg)
            self.stdout.flush()

    @transaction.commit_on_success
    def handle(self, *args, **options):
        self.force = options.get('force', False)
        self.quiet = options.get('quiet', False)

        # Get today's date
        today = datetime.date.today()

        if self.force or (today.day == 1):
            # Get the first of this month
            this_month = today.replace(day=1)

            # Get the first of last month
            try:
                last_month = today.replace(month=today.month-1, day=1)
            except ValueError:
                if today.month == 1:
                    last_month = today.replace(year=today.year-1, month=12, day=1)

            # Update the on sale flag for all products
            count = 0
            for p in Product.objects.all().order_by('title'):
                try:
                    current_price = p.prices.get(effective_date=this_month)
                    previous_price = p.prices.get(effective_date=last_month)

                    if current_price.amount < previous_price.amount:
                        p.on_sale = True

                        self.uprint('[SALE]: %s' % p)
                        count += 1
                    else:
                        p.on_sale = False

                    # Persist our changes
                    p.save()
                except ProductPrice.DoesNotExist:
                    pass

            self.uprint('\n%s items have dropped in price!' % count)
        else:
            self.uprint('\nToday is not the first of the month! Exiting ...')
