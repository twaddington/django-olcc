from olcc.models import ImportRecord

"""
Inject the last import date into the request context.
"""
def last_updated(request):
    try:
        return {
            'last_updated': ImportRecord.objects.latest().created_at
        }
    except ImportRecord.DoesNotExist:
        pass
