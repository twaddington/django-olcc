from django import forms

from olcc.models import Store

COUNTIES = (
    (u'baker', u'Baker'),
    (u'benton', u'Benton'),
    (u'clackamas', u'Clackamas'),
    (u'clatsop', u'Clatsop'),
    (u'columbia', u'Columbia'),
    (u'coos', u'Coos'),
    (u'crook', u'Crook'),
    (u'curry', u'Curry'),
    (u'deschutes', u'Deschutes'),
    (u'douglas', u'Douglas'),
    (u'gilliam', u'Gilliam'),
    (u'grant', u'Grant'),
    (u'harney', u'Harney'),
    (u'hood river', u'Hood River'),
    (u'jackson', u'Jackson'),
    (u'jefferson', u'Jefferson'),
    (u'josephine', u'Josephine'),
    (u'klamath', u'Klamath'),
    (u'lake', u'Lake'),
    (u'lane', u'Lane'),
    (u'lincoln', u'Lincoln'),
    (u'linn', u'Linn'),
    (u'malheur', u'Malheur'),
    (u'marion', u'Marion'),
    (u'morrow', u'Morrow'),
    (u'multnomah', u'Multnomah'),
    (u'polk', u'Polk'),
    (u'sherman', u'Sherman'),
    (u'tillamook', u'Tillamook'),
    (u'umatilla', u'Umatilla'),
    (u'union', u'Union'),
    (u'wallowa', u'Wallowa'),
    (u'wasco', u'Wasco'),
    (u'washington', u'Washington'),
    (u'wheeler', u'Wheeler'),
    (u'yamhill', u'Yamhill'))

class CountyForm(forms.Form):
    """
    A simple form containing a single choice field with a list
    of Oregon counties as choices.
    """
    county = forms.ChoiceField(label='By County', choices=COUNTIES,)
