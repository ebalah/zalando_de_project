import pytest

import zalando_de
from zalando_de.scrape import Scrapper, ArticleScrapper, ScrappingAssistant
from zalando_de.utils.logging import Logger


out_log =  f"{zalando_de.__path__[0]}\\unit_tests\\output_test_main.log"
output_dir = f"{zalando_de.__path__[0]}\\unit_tests\\output_data"


@pytest.fixture
def logger():
    return Logger(out_log)

def test_main_scrapper(logger):
    """
    Test scrapping all articles.
    """
    assistant = ScrappingAssistant(logger=logger)
    # The scrapper
    main_scrapper = Scrapper(assistant=assistant)
    # Start scrapping 3 articles
    main_scrapper.scrape(n_pages=2, n_articles=10)
    # save the scrapped data into a json file.
    main_scrapper.to_dict(output_dir)
    # Save the scrapped data into a csv file.
    main_scrapper.to_pandas(read_json=False,
                            save_to_csv=True,
                            output_dir=output_dir)