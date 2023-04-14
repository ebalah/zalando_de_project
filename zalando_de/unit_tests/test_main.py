import pytest
import traceback

import zalando_de
from zalando_de.scrape.main import Scraper, ScraperAssistant
from zalando_de.scrape.commun.exceptions import *
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

    log_dir = create_directory(f"{zalando_de.__path__[0]}/unit_tests/output/{hw}/logs", False)
    data_dir = create_directory(f"{zalando_de.__path__[0]}/unit_tests/output/{hw}/data", False)

    return Logger(f"{log_dir}/logging.log", 10), data_dir


@pytest.mark.parametrize('how', [
    # 'single',
    'all'
])
def test_scrape_all(how):
    """
    Test scrapping all articles.
    """

    links = LINKS.copy() if how == 'single' else []

    logger, data_output_dir = get_outputs(how)
    
    # Start Processing (Scrapping)
    with ScraperAssistant(logger=logger) as assistant:

        try:
            scraper = Scraper(assistant=assistant, out=data_output_dir)
            scraper.scrape(how, links)
            logger.info("Processing finished successfully.",
                        _lbr=True, _rbr=True)
            
        except KeyboardInterrupt:
            logger.error("Processing forcibly stopped using "
                        "keyboard : Ctrl + C",
                        _lbr=True, _rbr=True)
            logger.error(traceback.format_exc(), show_details=False)
            
        except (WindowAlreadyClosedException,
                UnableToConnectException) as exc:
            logger.error("Processing Failed with the following Error :",
                        _lbr=True, _rbr=True)
            exc.err()

        except BaseException as exc:
            logger.error("Processing Failed with the following Unknown Exception :",
                        _lbr=True, _rbr=True)
            logger.error(traceback.format_exc(), show_details=False)