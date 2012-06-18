from django import template

from bs4 import BeautifulSoup

register = template.Library()

@register.tag(name='activehref')
def do_active_href(parser, token):
    nodelist = parser.parse(('endactivehref',))
    parser.delete_first_token()
    return ActiveHref(nodelist)

class ActiveHref(template.Node):
    """
    This template tag will set an 'active' class attribute
    on any anchor with an href value that matches part of the
    current url path.

    Sample template usage:

    {% activehref %}
    <li><a href="{% url products %}">Products</a></li>
    <li><a href="{% url stores %}">Stores</a></li>
    <li><a href="{% url about %}">About</a></li>
    {% endactivehref %} 
    """
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        soup = BeautifulSoup(self.nodelist.render(context))

        if context.has_key('request'):
            path = context.get('request').path

            for a in soup.find_all('a'):
                href = a['href']

                if href == '/':
                    if path == href:
                        a['class'] = 'active'
                        break
                else:
                    if href in path:
                        a['class'] = 'active'
                        break

        return soup
