# StockTracker - A simple stock tracker

## Introduction
For the final 'Capstone' project of this web development course, I decided to create a simple stock tracker. Registered
users can add stocks, watch stocks and create portfolios to track their stocks and portfolio performance over time.
Django was used as back-end framework, while plain JavaScript, HTML and CSS were used for the front-end. Additionally,
the Tabulator library was used to create tables within the front-end.

## Distinctiveness & Complexity
The project is distinct from the other projects in this course as first of all, I chose for a very different application
of the acquired knowledge. For this reason, I could only reuse some basic aspects, like user registration and login. For
all other content, I had to start from scratch, as should be the case. I've started with some basic models and views,
which I continuously expanded upon. During the course of the project, I had to make quite some changes to the models, 
as can be seen from the migrations. This for me also proves that the project is distinct from the other projects, 
as due to its distinctiveness, I wasn't able to fully oversee the project at the start.

The project also ticks the boxes for complexity, as it comprises the most important aspects of the course:
- HTML & CSS
- Python, Django & SQL
- JavaScript

I believe that for all of these aspects, I've used the acquired knowledge to a proper extent, not 'avoiding' any of them:

- Regarding *HTML & CSS*, I've created quite some different templates for different pages with sufficient complexity, 
that also include some JavaScript to dynamically resize, fold and unfold a sidebar.
- Regarding *Python, Django & SQL*, I've created an appropriate number of models with sufficient complexity and mutual relations.
- Lastly, regarding *JavaScript*, I've created a `tracker.js` file that contains the JavaScript code to fetch data from
the back-end and visualize it in tabulated format within the front-end. This file also contains a JavaScript function that
dynamically updates the front-end after a successful PUT request to add or remove a stock watch.

To visualize the data in tabulated format, I make use of the Tabulator library, which is a JavaScript library that 
allows to easily create tables in the front-end. Working with such an additional library was an interesting additional 
challenge to the project, and it proved good fun to nicely format the tables. To that purpose, I created some custom
formatters that can be found within the `tableutils.js` file.

## Functionality
See below the folder structure of the Django project. The project is called *Stocks*, containing a *tracker* app.
After the folder and file names, I have indicated their use. Where I didn't change anything of the default Django file,
I've omitted the description.

```
- stocks
    - stocks
        - asgi.py
        - settings.py                   # Contains the settings for the project, with an additional local caching mechanism for exchange rates
        - urls.py                       # Contains the URL patterns for the project
        - wsgi.py
    - tracker
        - migrations                    # Folder with all model migrations
        - static
            - images                    # Folder with all icons within the sidebar
            - styles.css                # Contains the CSS styling for the project
            - tableutils.js             # Contains the custom formatters for the Tabulator tables
            - tracker.js                # Contains the code to fetch data from the back-end and visualize it in the front-end
        - templates
            - add_dividend.html         # Template for adding a dividend (either Stock- or FiatDividend)
            - add_portfolio.html        # Template for adding a portfolio
            - add_stock.html            # Template for adding a stock
            - add_transaction.html      # Template for adding a transaction (either Stock- or FiatTransaction)
            - index.html                # Template for the index page, showing a list of (watched) stocks, also contains a sidebar
            - layout.html               # Template for the layout of the website, also contains the navbar and JS functionality for the sidebar
            - login.html                # Template for the login page, this is very similar to those of other projects
            - portfolios.html           # Template for the portfolios page, showing the stocks within a portfolio, also contains a sidebar
            - profile.html              # Template for the profile page, showing the user's profile, also contains a sidebar
            - register.html             # Template for the registration page, this is very similar to those of other projects
        - admin.py                      # Contains the admin site configuration, basically registering all models
        - apps.py
        - models.py                     # Contains all models, an extended User model, Portfolio, Stock, StockWatch and transaction models
        - tests.py
        - urls.py                       # Contains the URL patterns for the app
        - utils.py                      # Contains a function to fetch exchange rates from the Open Exchange Rates API
        - views.py                      # Contains all views, including the API endpoints
    - db.sqlite3
    - manage.py
    - requirements.txt                  # Contains all required packages for the project (just Django and requests)
```

## How to run
Running the application is straightforward, simply run ```python stocks/manage.py runserver``` from the root of the project.