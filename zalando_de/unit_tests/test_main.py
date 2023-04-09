import pytest

import zalando_de
from zalando_de.scrape import Scraper, ScraperAssistant
from zalando_de.utils.logging import Logger


out_log =  f"{zalando_de.__path__[0]}/../output/logs/main_scraper_logging.log"
output_dir = f"{zalando_de.__path__[0]}/../output/data"


def get_logger():
    return Logger(out_log)

def test_main_scraper():
    """
    Test scrapping all articles.
    """
    logger = get_logger()
    # Define the assistant
    assistant = ScraperAssistant(logger=logger)
    # The scraper
    main_scraper = Scraper(assistant=assistant, out=output_dir)
    # Start scrapping 3 articles
    main_scraper.scrape(n_pages=3)
    # save the scrapped data into a json file.
    main_scraper.save_to_json()
    # Save the scrapped data into a csv file.
    # main_scraper.to_pandas(read_json=False,
    #                         save_to_csv=True,
    #                         output_dir=output_dir)