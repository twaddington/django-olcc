This project represents a Django site built for the sole
purpose of displaying [Oregon Liquor Control Commission (OLCC)][olcc]
product and price data.

The models are designed to easily import product data directly
from the OLCC and include enhanced functionality for interacting
with the original data set.

The project was born simply because the data existed and was freely
available. It also helps that the current OLCC price search website is
pretty unimpressive.

You can view the code running live at [oregonliquorprices.com][project-home].

## Contributors

You are encouraged to fork the project and add new functionality. We'd
love to see your pull requests! Please make sure to run tests before
submitting a patch.

    $ python manage.py test olcc

## Potential Features

- Product images: Scrape Creative Commons licensed photos or accept submissions.
- Price monitoring: Get notified when your favorite item drops in price.
- Price intelligence: Analyze historical price changes to predict future sales.

[olcc]: http://www.oregon.gov/OLCC/index.shtml
[project-home]: http://www.oregonliquorprices.com/
