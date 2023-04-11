import pytest
import traceback

import zalando_de
from zalando_de.scrape import Scraper, ScraperAssistant
from zalando_de.utils.logging import Logger
from zalando_de.utils.helpers import create_directory



LINKS = [
    'https://en.zalando.de/pier-one-shirt-dark-green-pi922d09r-m11.html',
    'https://en.zalando.de/olymp-no-six-formal-shirt-bleu-ol022d04g-k11.html',
    'https://en.zalando.de/sir-raymond-tailor-shirt-navy-bordeaux-sic22d03t-k12.html',
    'https://en.zalando.de/sir-raymond-tailor-shirt-khaki-sic22d03i-n11.html',
    'https://en.zalando.de/sir-raymond-tailor-shirt-navy-bordeaux-sic22d03t-k12.html', # Duplicated
    'https://en.zalando.de/olymp-no-six-formal-shirt-bleu-ol022d04g-k11.html', # Duplicated
    'https://en.zalando.de/pier-one-2pack-formal-shirt-whitelight-blue-pi922d05k-a11.html',
    'https://en.zalando.de/next-2-pack-formal-shirt-off-white-nx322d0zp-a11.html',
    'https://en.zalando.de/sir-raymond-tailor-shirt-khaki-sic22d03i-n11.html',  # Duplicated
]


def get_outputs(hw: str):

    log_dir = create_directory(f"{zalando_de.__path__[0]}/unit_tests/output/{hw}/logs", True)
    data_dir = create_directory(f"{zalando_de.__path__[0]}/unit_tests/output/{hw}/data", True)

    return Logger(f"{log_dir}/logging.log", 10), data_dir


@pytest.mark.parametrize('how', [
    'all',
    'single'
])
def test_scrape_all(how):
    """
    Test scrapping all articles.
    """

    links = LINKS.copy() if how == 'single' else []

    logger, data_dir = get_outputs(how)

    # Define the assistant
    with ScraperAssistant(logger=logger) as assistant:

        try:
            Scraper(assistant, data_dir).scrape(how, links)
            logger.info("Processing finished successfully.",
                        _lbr=True, _rbr=True)
            
        except KeyboardInterrupt:
                logger.error("Processing forcibly stopped using "
                             "keyboard: Ctrl+C",
                             _lbr=True, _rbr=True)
                logger.error(traceback.format_exc(), show_details=False)

        except Exception as e:
            if not (hasattr(e, 'msg__browser_closed_forcibly')
                    or hasattr(e, 'msg__internet_disconnected')):
                # This excepts the errors logging in case of one
                # of BROWSER_CLOSED_EXCEPTIONS is catched.
                logger.error("Processing Failed with an Error :",
                             _lbr=True, _rbr=True)
                logger.error(traceback.format_exc(), show_details=False)