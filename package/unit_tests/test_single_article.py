import pytest
import traceback
import json

from package.main import Scrapper
from package.utils.helpers import file_name_timer
from package.utils.logging import Logger

# units test dirictory
unit_test_dir = 'C:\\Users\\dsicped\\Desktop\\PS\\_09\\package\\unit_tests'

# Logging configuration
log_output = f"{unit_test_dir}\\test_single_article_{file_name_timer()}.log"
logger = Logger(log_output)

logger = Logger()


articles_link = [
    'https://en.zalando.de/pier-one-shirt-dark-green-pi922d09r-m11.html',
    'https://en.zalando.de/olymp-no-six-formal-shirt-bleu-ol022d04g-k11.html',
    'https://en.zalando.de/pier-one-2pack-formal-shirt-whitelight-blue-pi922d05k-a11.html',
    'https://en.zalando.de/next-2-pack-formal-shirt-off-white-nx322d0zp-a11.html',
    'https://en.zalando.de/sir-raymond-tailor-shirt-khaki-sic22d03i-n11.html',
    'https://en.zalando.de/sir-raymond-tailor-shirt-navy-bordeaux-sic22d03t-k12.html'
]


def save_to_json(data: list[dict]):
    """ save to json file """
    try :
        with open(f"{unit_test_dir}\\data\\articles_sample_5.json", 'r+', encoding='utf-8') as json_file:
            to_add_data = json.load(json_file)
            to_add_data.append(data)
    except FileNotFoundError as e:
        to_add_data = [data]

    with open(f"{unit_test_dir}\\data\\articles_sample_5.json", 'w+', encoding='utf-8') as json_file:
        json.dump(to_add_data, json_file, indent=3, ensure_ascii=False)


@pytest.fixture(scope='session')
def scrapper():
    return Scrapper(logger)


@pytest.mark.parametrize('article_link', articles_link)
def test_single_article(article_link, scrapper: Scrapper):
    """
    Test the functionalties of the Scrapper.get
    
    """
    # Get the details
    try:
        article_details = scrapper.scrape_single_article(article_link)
        # save 
        save_to_json(article_details)
    except Exception as e:
        logger.log(traceback.format_exc())