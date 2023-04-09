import pytest
import traceback
import json

import zalando_de
from zalando_de.scrape import Scraper, ScraperAssistant
from zalando_de.utils.logging import Logger


out_log =  f"{zalando_de.__path__[0]}\\..\\output\\logs\\main_article_logging.log"
output_dir = f"{zalando_de.__path__[0]}\\..\\output\\data"


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


def save_to_json(data: list):
    """ save to json file """
    with open(f"{output_dir}\\articles_sample.json", 'w+', encoding='utf-8') as json_file:
        json.dump(data,
                  json_file,
                  indent=3,
                  ensure_ascii=False)


def get_scraper():
    logger = get_logger()
    assistant = ScraperAssistant(logger=logger)
    return Scraper(assistant, out=output_dir)


@pytest.mark.parametrize('articles_link', articles_link)
def test_article_scraper(articles_link):
    """
    Test the functionalties of the scraper.get
    
    """
    scraper = get_scraper()
    # Get the details
    try:
        article_details = scraper.scrape_articles(articles_link)
        # save 
        save_to_json(article_details)
    except Exception as e:
        scraper._sa.logger.error(traceback.format_exc(), show_details=False)