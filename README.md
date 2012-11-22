This project represents a Django site built for the sole
purpose of displaying [Oregon Liquor Control Commission (OLCC)][1]
product, price and store data.

The models are designed to easily import product data directly
from the OLCC and include enhanced functionality for interacting
with the original data set.

The project was born simply because the data existed and was freely
available.

You can view the live site at [oregonliquorprices.com][2].

## OLCC Excel files

- http://www.olcc.state.or.us/pdfs/Numeric_Price_List_Next_Month.xls
- http://www.olcc.state.or.us/pdfs/Numeric_Price_List_Current.xls
- http://www.olcc.state.or.us/pdfs/PriceHistory_Excel.xls

## Contributors

You are encouraged to fork the project and add new functionality. We'd
love to see your pull requests! Please make sure to run tests before
submitting a patch.

    $ python manage.py test olcc

Please make sure your editor is configured to use the proper indentation
style with 4-spaces and no tab characters.

## Getting Started

After cloning the project into your python virtualenv, you'll first need
to create a basic `settings_local.py` with the following contents:

    DEBUG = True
    TEMPLATE_DEBUG = True

Active your virtualenv and install the project dependencies:

    $ pip install -r requirements.txt

To start the local development server simply run:

    $ python manage.py run_gunicorn

You'll then need to create your local development database by running:

    $ python manage.py syncdb

A development fixture has been provided to get you up and running
quickly. You can import this fixture by running:

    $ python manage.py loaddata olccdev

You can import fresh product data into your database by running:

    $ python manage.py olccfetch

## Potential Features

- Price calculator: Per shot, oz, ml, 2oz bar pour.
- Collapse product sizes onto a single detail page. This could potentially be
  done using the product code, which seem to have a common prefix for product
  type.
- Find stores by proximity to the visitor's current location.
- Parse the store hours into a machine readable format. Display stores as
  currently open/closed.
- Product images: Scrape Creative Commons licensed photos or accept submissions.
- Price monitoring: Get notified when your favorite item drops in price or is
  about to go up in price.
- Price intelligence: Analyze historical price changes to predict future sales.

[1]: http://www.oregon.gov/OLCC/index.shtml
[2]: http://www.oregonliquorprices.com/
[3]: https://toolbelt.herokuapp.com/
