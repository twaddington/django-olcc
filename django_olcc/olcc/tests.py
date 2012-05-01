import requests

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from mock import Mock, patch

from olcc.models import ProductImport
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
        self.mock_head_response.headers = {'ETag': self.etags[0]}

        self.mock_get_response = Mock(requests.Response)
        self.mock_get_response.text = "baz"

    def test_command(self, mock_head, mock_get, mock_command):
        """
        Test the command when there is no pre-existing ProductImport
        records found.
        """
        mock_get.return_value = self.mock_get_response

        # Sanity check
        self.assertEqual(ProductImport.objects.count(), 0)
        
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
        pi = ProductImport.objects.all()
        self.assertEqual(pi.count(), 1)
        self.assertEqual(pi[0].url, self.default_url)

    def test_command_etag(self, mock_head, mock_get, mock_command):
        """
        Test the command when there is an existing ProductImport
        record.
        
        We are particular interested in verifying that the command will
        correctly match ETag values and determine if the remote file
        has changed.
        """
        mock_get.return_value = self.mock_get_response

        # Sanity check
        self.assertEqual(ProductImport.objects.count(), 0)

        # Set up our response headers
        etag = self.etags[0]
        mock_head.return_value = self.mock_head_response
        mock_head.return_value.headers.update({'ETag': etag})

        # Create a new ProductImport record
        pi = ProductImport()
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

        # Prepare our Mock response object to return a new ETag
        etag = self.etags[1]
        mock_head.reset_mock()
        mock_head.return_value = self.mock_head_response
        mock_head.return_value.headers.update({'ETag': etag})

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
        flag is set regardless of the ETag returned.
        """
        mock_get.return_value = self.mock_get_response

        # Sanity check
        self.assertEqual(ProductImport.objects.count(), 0)

        # Set up our response headers
        etag = self.etags[0]
        mock_head.return_value = self.mock_head_response
        mock_head.return_value.headers.update({'ETag': etag})

        # Create a new ProductImport record
        pi = ProductImport()
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
        self.assertEqual(ProductImport.objects.count(), 0)

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
    def test_smoke(self):
        pass
