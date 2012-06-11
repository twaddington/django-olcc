import datetime
import requests
import xlrd

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from mock import Mock, patch

from olcc.models import ImportRecord, Store, Product, ProductPrice
from olcc.management.commands import olccfetch

@patch('olcc.management.commands.olccfetch.call_command')
@patch.object(requests, 'get')
@patch.object(requests, 'head')
class TestFetchCommand(TestCase):
    def setUp(self):
        self.default_url = getattr(settings, 'OLCC_PRICE_LIST_URL')
        self.etags = ('"foo"', '"bar"')

        # Configure our Mock HTTP response
        self.mock_head_response = Mock(requests.Response)
        self.mock_head_response.headers = {'etag': self.etags[0]}

        self.mock_get_response = Mock(requests.Response)
        self.mock_get_response.text = "baz"
        self.mock_get_response.content = "baz"

    def test_command(self, mock_head, mock_get, mock_command):
        """
        Test the command when there is no pre-existing ImportRecord
        records found.
        """
        mock_get.return_value = self.mock_get_response

        # Sanity check
        self.assertEqual(ImportRecord.objects.count(), 0)
        
        # Invoke our management command
        call_command('olccfetch', quiet=True)

        # Ensure our command made a head request to the
        # default URL.
        self.assertTrue(mock_head.called)
        self.assertEqual(mock_head.call_count, 1)
        self.assertEqual(mock_head.call_args[0][0], self.default_url)

        # Ensure our command made a get request to the
        # default URL.
        self.assertTrue(mock_get.called)
        self.assertEqual(mock_get.call_count, 1)
        self.assertEqual(mock_get.call_args[0][0], self.default_url)

        # Ensure our command called through to 'olccimport' with
        # a path to a temp file.
        self.assertTrue(mock_command.called)
        self.assertEqual(mock_command.call_count, 1)

        # Verify the correct import command was invoked
        name = mock_command.call_args[0][0]
        self.assertEqual(name, 'olccimport')

        # Verify that the tempfile was written with the response value
        path = mock_command.call_args[0][1]
        with open(path, 'r') as f:
            self.assertEqual(f.read(), self.mock_get_response.text)

        # Verify that a product import record was created
        pi = ImportRecord.objects.all()
        self.assertEqual(pi.count(), 1)
        self.assertEqual(pi[0].url, self.default_url)

    def test_command_etag(self, mock_head, mock_get, mock_command):
        """
        Test the command when there is an existing ImportRecord
        record.
        
        We are particular interested in verifying that the command will
        correctly match etag values and determine if the remote file
        has changed.
        """
        mock_get.return_value = self.mock_get_response

        # Sanity check
        self.assertEqual(ImportRecord.objects.count(), 0)

        # Set up our response headers
        etag = self.etags[0]
        mock_head.return_value = self.mock_head_response
        mock_head.return_value.headers.update({'etag': etag})

        # Create a new ImportRecord record
        pi = ImportRecord()
        pi.etag = etag.strip('"')
        pi.url = self.default_url
        pi.save()

        # Invoke our management command. We should not expect it to
        # run an import since the etag of the previous import record
        # and the etag returned from the head request are the same.
        call_command('olccfetch', quiet=True)

        # Ensure our command made a head request to the
        # default URL.
        self.assertTrue(mock_head.called)
        self.assertEqual(mock_head.call_count, 1)
        self.assertEqual(mock_head.call_args[0][0], self.default_url)

        # Ensure our command *did not* make a get request to the
        # default URL.
        self.assertFalse(mock_get.called)

        # Ensure our command *did not* call through to 'olccimport'
        self.assertFalse(mock_command.called)

        # Prepare our Mock response object to return a new etag
        etag = self.etags[1]
        mock_head.reset_mock()
        mock_head.return_value = self.mock_head_response
        mock_head.return_value.headers.update({'etag': etag})

        # Invoke our management command. We should now expect it
        # to run an import and behave opposite to the previous case.
        call_command('olccfetch', quiet=True)

        # Ensure our command made a head request to the
        # default URL.
        self.assertTrue(mock_head.called)
        self.assertEqual(mock_head.call_count, 1)
        self.assertEqual(mock_head.call_args[0][0], self.default_url)

        # Ensure our command made a get request to the
        # default URL.
        self.assertTrue(mock_get.called)
        self.assertEqual(mock_get.call_count, 1)
        self.assertEqual(mock_get.call_args[0][0], self.default_url)

        # Verify that our import command was now called
        self.assertTrue(mock_command.called)

    def test_force(self, mock_head, mock_get, mock_command):
        """
        Verify that the command will run an import when the force
        flag is set regardless of the etag returned.
        """
        mock_get.return_value = self.mock_get_response

        # Sanity check
        self.assertEqual(ImportRecord.objects.count(), 0)

        # Set up our response headers
        etag = self.etags[0]
        mock_head.return_value = self.mock_head_response
        mock_head.return_value.headers.update({'etag': etag})

        # Create a new ImportRecord record
        pi = ImportRecord()
        pi.etag = etag.strip('"')
        pi.url = self.default_url
        pi.save()

        # Invoke our management command. We should not expect it to
        # run an import since the etag of the previous import record
        # and the etag returned from the head request are the same.
        call_command('olccfetch', quiet=True, force=False)

        # Ensure our command made a head request to the
        # default URL.
        self.assertTrue(mock_head.called)
        self.assertEqual(mock_head.call_count, 1)
        self.assertEqual(mock_head.call_args[0][0], self.default_url)

        # Ensure our command *did not* make a get request to the
        # default URL.
        self.assertFalse(mock_get.called)

        # Ensure our command *did not* call through to 'olccimport'
        self.assertFalse(mock_command.called)

        # Retry the request with the force flag updated
        call_command('olccfetch', quiet=True, force=True)
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_command.called)

    def test_url(self, mock_head, mock_get, mock_command):
        """
        Verify that the command uses the provided URL instead of
        the default.
        """
        mock_get.return_value = self.mock_get_response

        # Sanity check
        self.assertEqual(ImportRecord.objects.count(), 0)

        # Invoke our management command
        url = "http://example.com/"
        call_command('olccfetch', quiet=True, url=url)

        # Ensure our command made a head request to the
        # default URL.
        self.assertTrue(mock_head.called)
        self.assertEqual(mock_head.call_count, 1)
        self.assertEqual(mock_head.call_args[0][0], url)

        # Ensure our command made a get request to the
        # default URL.
        self.assertTrue(mock_get.called)
        self.assertEqual(mock_get.call_count, 1)
        self.assertEqual(mock_get.call_args[0][0], url)

        # Ensure our command called through to 'olccimport' with
        # a path to a temp file.
        self.assertTrue(mock_command.called)
        self.assertEqual(mock_command.call_count, 1)

        # Verify the correct import command was invoked
        name = mock_command.call_args[0][0]
        self.assertEqual(name, 'olccimport')

        # Verify that the tempfile was written with the response value
        path = mock_command.call_args[0][1]
        with open(path, 'r') as f:
            self.assertEqual(f.read(), self.mock_get_response.text)

    def test_quiet(self, mock_head, mock_get, mock_command):
        """
        :todo: Test the quiet flag.
        """
        pass


class TestImportCommand(TestCase):
    def setUp(self):
        self.stores = [
            (12345, 'First', '(842) 123-4567', 'Address', 'Hours', 'County'),
            (54321, 'Second', '(503) 123-4567', 'Address', 'Hours', 'County'),
            (12321, 'Third', '(541) 123-4567', 'Address', 'Hours', 'County'),
        ]

        self.prices = [
            ('0102B', '@', 'GLENFIDDICH SNOW PHOENIX', '750 ML', 6, 92.95),
            ('0103B', '', 'BALVENIE 14 YR CARIBBEAN C', '750 ML', 6, 64.95),
            ('0105B', '', 'DECO COFFEE RUM', '750 ML', 12, 23.95),
        ]

        self.history = [
            ('2012', '7', '1241B', 'SWEET BABY MOONSHINE', '750 ML', 0, None, 95.00, 12, 25.95),
            ('2012', '7', '1243B', 'WARSHIP SILVER RUM 125 PRO', '', 0, None, 125.00, 12, 24.95),
            ('2012', '6', '0103B', 'BALVENIE 14 YR CARIBBEAN C', '', 14, None, 86.00, 6, 69.95),
            ('2011', '7', '1241B', 'SWEET BABY MOONSHINE', '750 ML', 0, None, 95.00, 12, 15.95),
            ('2011', '7', '1243B', 'WARSHIP SILVER RUM 125 PRO', '', 0, None, 125.00, 12, 14.95),
            ('2011', '6', '0103B', 'BALVENIE 14 YR CARIBBEAN C', '', 14, None, 86.00, 6, 39.95),
        ]

    def test_validation(self):
        """
        Verify the command throws the proper exceptions when
        required *args are missing.
        """
        # Test missing filename
        try:
            print "\nTest Output: Ignore Error"
            self.assertRaises(CommandError,
                    call_command, 'olccimport', quiet=True)
        except SystemExit:
            pass

        # Test invalid filename
        try:
            print "Test Output: Ignore Error"
            self.assertRaises(CommandError,
                    call_command, 'olccimport', '/foo/bar/baz.xls', quiet=True)
        except SystemExit:
            pass

    @patch.object(xlrd, 'open_workbook')
    def test_import_stores(self, mock_open_workbook):
        """
        Test a basic stores file import.
        """
        # Configure our Mocks
        sheet_mock = Mock()
        sheet_mock.nrows = len(self.stores)
        sheet_mock.row_values = Mock(side_effect=self.stores)

        wb_mock = Mock(return_value=sheet_mock)
        wb_mock.sheet_by_index = Mock(return_value=sheet_mock)

        mock_open_workbook.return_value = wb_mock

        # Sanity check
        self.assertEqual(Store.objects.count(), 0)

        # Call our management command
        path = '/foo/bar/baz.xml'
        call_command('olccimport', path, quiet=True, import_type='stores',
                geocode=False)

        # Verify open_workbook was called correctly
        self.assertTrue(mock_open_workbook.called)
        self.assertEqual(mock_open_workbook.call_count, 1)
        self.assertEqual(mock_open_workbook.call_args[0][0], path)

        # Verify the expected number of Store objects were created
        stores = Store.objects.all()
        self.assertEqual(stores.count(), len(self.stores))

        # Verify the store data
        i = 0
        for s in stores:
            self.assertEqual(self.stores[i][0], s.key)
            self.assertEqual(self.stores[i][1], s.name.split()[0])
            self.assertEqual(self.stores[i][2], s.phone)
            self.assertEqual(self.stores[i][3], s.address)
            self.assertEqual(self.stores[i][4], s.hours_raw)
            self.assertEqual(self.stores[i][5], s.county)
            self.assertEqual(s.address, s.address_raw)
            i += 1

    @patch.object(xlrd, 'open_workbook')
    def test_import_prices(self, mock_open_workbook):
        """
        Test a basic prices file import.
        """
        # Configure our Mocks
        sheet_mock = Mock()
        sheet_mock.nrows = len(self.prices)
        sheet_mock.row_values = Mock(side_effect=self.prices)

        wb_mock = Mock(return_value=sheet_mock)
        wb_mock.sheet_by_index = Mock(return_value=sheet_mock)

        mock_open_workbook.return_value = wb_mock

        # Sanity check
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductPrice.objects.count(), 0)

        # Call our management command
        path = 'foo/bar/baz/xml'
        call_command('olccimport', path, quiet=True, import_type='prices',)

        # Verify open_workbook was called correctly
        self.assertTrue(mock_open_workbook.called)
        self.assertEqual(mock_open_workbook.call_count, 1)
        self.assertEqual(mock_open_workbook.call_args[0][0], path)

        # Verify the expected number of objects were created
        products = Product.objects.all().order_by('pk')
        self.assertEqual(products.count(), len(self.prices))

        prices = ProductPrice.objects.all().order_by('pk')
        self.assertEqual(prices.count(), len(self.prices))

        # Calculate the expected price date
        today = datetime.date.today()
        try:
            price_date = today.replace(month=today.month+1, day=1)
        except ValueError:
            if today.month == 12:
                price_date = today.replace(year=today.year+1, month=1, day=1)

        # Verify the product data
        i = 0
        for p in products:
            self.assertEqual(self.prices[i][0], p.code)
            self.assertEqual(self.prices[i][1], p.status)
            self.assertEqual(self.prices[i][2], p.title.upper())
            self.assertEqual(self.prices[i][3], p.size)
            self.assertEqual(self.prices[i][4], p.bottles_per_case)
            self.assertEqual(p.prices.count(), 1)

            # Verify the price data
            price = p.prices.all()[0]
            self.assertEqual(price.effective_date, price_date)

            # Increment the counter
            i += 1

    @patch.object(xlrd, 'open_workbook')
    def test_import_price_history(self, mock_open_workbook):
        """
        Test a basic price history file import.
        """
        # Configure our Mocks
        sheet_mock = Mock()
        sheet_mock.nrows = len(self.history)
        sheet_mock.row_values = Mock(side_effect=self.history)

        wb_mock = Mock(return_value=sheet_mock)
        wb_mock.sheet_by_index = Mock(return_value=sheet_mock)

        mock_open_workbook.return_value = wb_mock

        # Sanity check
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductPrice.objects.count(), 0)

        # Call our management command
        path = 'foo/bar/baz/xml'
        call_command('olccimport', path, quiet=True, import_type='price_history',)

        # Verify open_workbook was called correctly
        self.assertTrue(mock_open_workbook.called)
        self.assertEqual(mock_open_workbook.call_count, 1)
        self.assertEqual(mock_open_workbook.call_args[0][0], path)

        # Verify the expected number of objects were created
        products = Product.objects.all().order_by('pk')
        self.assertEqual(products.count(), len(self.history) / 2)

        prices = ProductPrice.objects.all().order_by('pk')
        self.assertEqual(prices.count(), len(self.history))

        # Verify the product data
        i = 0
        for p in products:
            self.assertEqual(self.history[i][2], p.code)
            self.assertEqual(self.history[i][3], p.title.upper())
            self.assertEqual(self.history[i][4], p.size)
            self.assertEqual(self.history[i][5], p.age)
            self.assertEqual(self.history[i][7], p.proof)
            self.assertEqual(p.prices.count(), 2)

            # Calculate the expected price data
            price_date = datetime.date(int(self.history[i][0]),
                    int(self.history[i][1]), 1)

            # Verify the price data
            price = p.prices.all()[0]
            self.assertEqual(price.effective_date, price_date)

            # Increment the counter
            i += 1

class TestPeriodicCommand:
    def test_smoke(self):
        """
        """
        pass
