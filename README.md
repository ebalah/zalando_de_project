# Notes

The project deliverable is a python package created specifically to scrape data from `zalando.de` website.

__NB__ : It is preferable to use either `Python 3.10.10` or `Python 3.8.10`.

# Instructions

## Environement Preparation (`On Windows`)

<br>

- Unzip the `zalando_de_project.zip` and Open a terminal.

- Change directory to the main folder `zalando_de_project/`.

- Create a virtual environment ( e.g. `python -m venv ./py_venv` ).

- Activate the created environment ( e.g. `& ./py_venv/Scripts/Activate.ps1` ).

- Install the package ( e.g. `pip install .` ). 

4 - Test the environment ( e.g. `pytest zalando_de/unit_tests -rA` ).

## Environement Preparation (`On Ubuntu/Linux`)

- Unzip the `zalando_de_project.zip` and Open a terminal.

- Change directory to the main folder `zalando_de_project/`.

- Create a virtual environment ( e.g. `python3 -m venv ./py_venv` ).

- Activate the created environment ( e.g. `source ./py_venv/bin/activate` ).

- Install the package ( e.g. `pip3 install .` ).

6 - Test the environment ( e.g. `pytest zalando_de/unit_tests -rA` ). 

# Description

__NB 1__ : The script is not complete yet.

In high-level, we have two main scrapping objects :

1 - Main Scraper : This is the user interface to call to start scrapping.
It has multiple methods to use :

- `scrape(n_pages=1, n_articles=1)` : by calling this method you can scrape n pages and n articles from each page.
- `save_to_json()` : This method is the main method used to save the scraped data. It saves the scrapped details in a json file `see output_test_py_3_8_10/data/scraped_details_20230409_124055.json`, and it saves the scraped products' links in another json file (note this is intended to help us to identify the artiles) `see output_test_py_3_8_10/data/scraped_articles.json`.
- `to_table()` : To be improved to read all the json file and combine the data to a csv file.

- `scrape_articles(links)` : This method is created to be used to scrape articles independetly using their links in cass any article was missed to be scraped using the Main Scraper.

2 - Article Scraper : This object is not used by the user directly, but it called from Main Scrapper to scrape a single article.

__NB 2__ : In this description we mean by article a men's Shirt product.

__NB 3__ : All the scrapping steps are traced and saved in log files. For example, see `output_test_py_3_8_10/logs/main_scraper_logging.log`.


