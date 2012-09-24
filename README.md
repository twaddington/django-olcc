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

To run the local development server you should first install the
[Heroku toolbelt][3]. You should then be able to start up
the Gunicorn server by running `foreman start` in the `src`
directory. Make sure you run `$ pip install requirements.txt` in
your virtualenv first. Alternatively, simply run the following from within
your virtualenv:

    $ python django_olcc/manage.py run_gunicorn

## Potential Features

- Find stores by proximity to the visitor's current location.
- Parse the store hours into a machine readable format. Display stores as
  currently open/closed.
- Product images: Scrape Creative Commons licensed photos or accept submissions.
- Price monitoring: Get notified when your favorite item drops in price.
- Price intelligence: Analyze historical price changes to predict future sales.

[1]: http://www.oregon.gov/OLCC/index.shtml
[2]: http://www.oregonliquorprices.com/
[3]: https://toolbelt.herokuapp.com/
