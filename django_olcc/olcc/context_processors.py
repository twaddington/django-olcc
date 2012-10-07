from olcc.models import ImportRecord

"""
Inject the last import date into the request context.
"""
def last_updated(request):
    record = ImportRecord.objects.latest()
    if record:
        return {
            'last_updated': record.created_at
        }
