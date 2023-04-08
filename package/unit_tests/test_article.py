import pytest
import traceback
import json

import package
from package.scrape import Scrapper, ScrappingAssistant
from package.utils.helpers import file_name_timer
from package.utils.logging import Logger


out_log =  f"{package.__path__[0]}\\unit_tests\\output_test_article.log"
output_dir = f"{package.__path__[0]}\\unit_tests\\output_data"


articles_link = [[
    'https://en.zalando.de/pier-one-shirt-dark-green-pi922d09r-m11.html',
    'https://en.zalando.de/olymp-no-six-formal-shirt-bleu-ol022d04g-k11.html',
    'https://en.zalando.de/pier-one-2pack-formal-shirt-whitelight-blue-pi922d05k-a11.html',
    'https://en.zalando.de/next-2-pack-formal-shirt-off-white-nx322d0zp-a11.html',
    'https://en.zalando.de/sir-raymond-tailor-shirt-khaki-sic22d03i-n11.html',
    'https://en.zalando.de/sir-raymond-tailor-shirt-navy-bordeaux-sic22d03t-k12.html'
]]


def get_logger():
    return Logger(out_log)


def save_to_json(data: list[dict]):
    """ save to json file """
    with open(f"{output_dir}\\articles_sample.json", 'w+', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=3, ensure_ascii=False)


@pytest.fixture(scope='module')
def scrapper():
    logger = get_logger()
    assistant = ScrappingAssistant(logger=logger)
    return Scrapper(assistant)


@pytest.mark.parametrize('articles_link', articles_link)
def test_article_scrapper(articles_link, scrapper: Scrapper):
    """
    Test the functionalties of the Scrapper.get
    
    """
    # Get the details
    try:
        article_details = scrapper.scrape_articles(articles_link)
        # save 
        save_to_json(article_details)
    except Exception as e:
        scrapper._sa.logger.log(traceback.format_exc())