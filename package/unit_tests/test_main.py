import pytest

import package
from package.scrape.main import Scrapper
from package.scrape.commun.assistants import ScrappingAssistant
from package.utils.logging import Logger


out_log =  f"{package.__path__[0]}\\unit_tests\\output_test.log"
output_dir = f"{package.__path__[0]}\\unit_tests\\output_data"


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
    main_scrapper.start(n_pages=2, n_articles=1)
    # # Get the results
    results = main_scrapper.to_dict(output_dir)

    # print(results)