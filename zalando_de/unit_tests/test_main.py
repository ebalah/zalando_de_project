import pytest

import zalando_de
from zalando_de.scrape import Scraper, ScraperAssistant
from zalando_de.utils.logging import Logger


LOG =  f"{zalando_de.__path__[0]}/../output/logs/logging.log"
DATA = f"{zalando_de.__path__[0]}/../output/data"


LINKS = ['https://en.zalando.de/pier-one-shirt-dark-green-pi922d09r-m11.html',
        'https://en.zalando.de/olymp-no-six-formal-shirt-bleu-ol022d04g-k11.html',
        'https://en.zalando.de/pier-one-2pack-formal-shirt-whitelight-blue-pi922d05k-a11.html',
        'https://en.zalando.de/next-2-pack-formal-shirt-off-white-nx322d0zp-a11.html',
        'https://en.zalando.de/sir-raymond-tailor-shirt-khaki-sic22d03i-n11.html',
        'https://en.zalando.de/sir-raymond-tailor-shirt-navy-bordeaux-sic22d03t-k12.html']


@pytest.fixture(scope="session")
def logger():
    return Logger(LOG, 1)


@pytest.mark.parametrize('how', [
    'single',
    'all'
])
def test_scrape_all(logger: Logger, how):
    """
    Test scrapping all articles.
    """
    links = LINKS.copy() if how == 'single' else []
    # Define the assistant
    with ScraperAssistant(logger=logger) as assistant:
        # The scraper
        try:
            Scraper(assistant=assistant, out=DATA).scrape(how, links)
            logger.info("Processing finished successfully.",
                        _lbr=True, _rbr=True)
        except Exception as e:
            if (hasattr(e, 'reason_why') and
                    e.reason_why == "BrowserClosedForcibly"):
                logger.info("Processing finished ( Probably the "
                            "Internet connection is lost, or the "
                            "browser is closed forcibly closed ).",
                            _lbr=True, _rbr=True)
            else:
                logger.info("Processing Failed with an Error :",
                            _lbr=True, _rbr=True)
                raise e