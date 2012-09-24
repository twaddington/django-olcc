import os
import requests
import tempfile

from optparse import make_option

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from olcc.models import ImportRecord
from olcc.management.commands.olccimport import IMPORT_TYPES

class Command(BaseCommand):
    help = """\
        Download a new file from the given URL and save it to the temp
        directory. The file should be in the format of an Excel spreadsheet
        containing an OLCC price list, price history or store list.
        If the file has changed since it was last fetched, a new import
        will be started."""

    option_list = BaseCommand.option_list + (
        make_option('--quiet', action='store_true', dest='quiet',
            default=False, help='Suppress all output except errors'),
        make_option('--force', action='store_true', dest='force',
            default=False, help='Ignore any ETag and force the import.'),
        make_option('--url', action='store', type='string', dest='url',
            help='The URL from where to fetch the file.'),
        make_option('--import-type', choices=IMPORT_TYPES,
            dest='import_type', default='prices',
            help='One of the following: %s' % (', '.join(IMPORT_TYPES),)),
    )

    def uprint(self, msg):
        """
        Unbuffered print.
        """
        if not self.quiet:
            self.stdout.write("%s\n" % msg)
            self.stdout.flush()

    def handle(self, *args, **options):
        self.quiet = options.get('quiet', False)
        force = options.get('force', False)
        url = options.get('url')
        import_type = options.get('import_type')

        if not url:
            # Get default URL from settings!
            url = getattr(settings, 'OLCC_PRICE_LIST_URL')

        try:
            previous_import = None
            try:
                previous_import = ImportRecord.objects.filter(\
                        url=url).latest('created_at')
            except ImportRecord.DoesNotExist:
                pass

            # Make a HEAD request for the given URL
            r = requests.get(url, timeout=5, prefetch=False)

            # Get the ETag for the resource
            etag = ""
            if r.headers.has_key('etag'):
                etag = r.headers.get('etag')
                etag = etag.strip('"')
            else:
                print "The server did not include an ETag in the response!"

            # Determine if we should run the import
            should_import = False

            if not previous_import or (etag != previous_import.etag):
                should_import = True

            if should_import or force:
                self.uprint('Starting import from:\n\t"%s"' % url)

                # Create a temp file
                fd, path = tempfile.mkstemp()

                with os.fdopen(fd, 'wb') as f:
                    # Write to the temp file
                    f.write(r.content)

                    # Create new import record
                    new_import = ImportRecord()
                    new_import.url = url
                    new_import.etag = etag
                    new_import.save()

                # Start a new import. This must be done outside of the
                # context manager block above, so that the file handle
                # can be fully closed before 'olccimport' tries to
                # open a new one.
                call_command('olccimport', path, import_type=import_type,
                        quiet=self.quiet)
            else:
                self.uprint("File not modified, skipping import.")
        except requests.exceptions.MissingSchema:
            print "Request failed! Invalid URL."
        except requests.ConnectionError:
            print "Request failed! ConnectionError."
        except requests.HTTPError:
            print "Request failed! HTTPError."
        except requests.Timeout:
            print "Request failed! Timeout."
        except requests.TooManyRedirects:
            print "Request failed! TooManyRedirects."
