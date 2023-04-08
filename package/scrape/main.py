import traceback

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException

import json

from package.utils.helpers import *
from package.scrape.commun.assistants import ScrappingAssistant
from package.scrape.units.article import ArticleScrapper



ALIEN_LINKS = ['/outfits/', '/collections/', '/men/']


class Scrapper():

    def __init__(self, assistant) -> None:
        # Logging configuration.
        self._sa: ScrappingAssistant = self.__validate_assistant(assistant)
        # Log the initiation of the scrapper
        self._sa.logger.log("Initiate the scrapper object.", 'INFO', _br=True)
        # Main link
        self.main_link = "https://en.zalando.de/mens-clothing-shirts/"
        # Scrapped data
        self.scrapped_data = {}
        # Metadata
        self._metadata = {}

    # NOTE: This needs to be improved.
    def __validate_assistant(self, assistant):
        return assistant

    def _handle_cookies(self, accept=False,
                        get_link: bool = False):
        """
        Accept cookies popup.
        
        """
        # If get_link, then get the driver to the main link
        if get_link:
            self._sa.driver.get(self.main_link)
        # Wait for the dialog presence.
        try:
            self._sa.xlong_wait.until(ec.visibility_of_element_located((By.ID, 'uc-main-banner')),
                                      message='Cookies did not poped up.')
            # Get the dialog
            popup = self._sa.driver.find_element(By.ID, "uc-main-banner")
            # Get the accept button.
            handle_button = (popup.find_element(By.ID, "uc-btn-accept-banner")
                            if accept
                            else popup.find_element(By.ID, 'uc-btn-deny-banner'))
            # Click the accept button
            ActionChains(self._sa.driver).move_to_element(popup).click(handle_button).perform()
            # Wait the disapearence of the dialog.
            self._sa.long_wait.until_not(ec.presence_of_element_located((By.ID, "uc-btn-accept-banner")))
            self._sa._sleep_t_sec()
        except TimeoutException as e:
            if e.msg != 'Cookies did not poped up.': raise e

    def _save_page_details(self):
        """
        Get the current page's details, and save them to metadata.
        
        Intended to be called only when the driver is on the
        main page.

        """
        # Total items
        class_names = '_0Qm8W1 _7Cm1F9 FxZV-M weHhRC u-6V88 FxZV-M'
        total_items = clean_text_number(self._sa._get_element_value_by_class(class_names))
        # Total pages
        class_names = '_0Qm8W1 _7Cm1F9 FxZV-M pVrzNP JCuRr_ _0xLoFW uEg2FS FCIprz'
        _, total_pages = clean_pagination_label(self._sa._get_element_value_by_class(class_names))
        # Save the values into the scrapper's metadata
        self.save_metadata({'total_pages': total_pages,
                            'total_items': total_items})
        # Return the details
        return total_items, total_pages
    
    def _curr_url(self):
        """
        Get the currently opened page's url.

        """
        return self._sa.driver.current_url

    def _next_page(self):
        """
        Find the next page's button, and check if it is disabled.
        If so, return False, otherwise return True.
        
        """
        # Get the next btn element
        next_btn = self._sa._get_elements_by_class('DJxzzA OldB32')[-1]
        # If the btn is enabled (i.e. there is another page), click it,
        # wait th new page to load, and return True.
        if next_btn.is_enabled():
            # Click the btn
            self._sa._move_mouse_to_and_click(next_btn)
            # Wait the page to load
            self._sa._wait_to_load()
            # Return the enablity of the next page.
            return True
        # Otherwise, return False, indicating there is no more pages.
        return False
    
    def _is_alien_link(self, link: str):
        """
        Verify if a link is alien or not.
        
        """
        # Search if there is any alien string in the link.
        for alien in ALIEN_LINKS:
            # If so, return True
            if alien in link:
                return True
        # Otherwise, return False
        return False
    
    def _is_an_article_link(self, link: str):
        """
        Verify if the the actual opened page is for an article.
        
        """
        # Verify if the link is alien, and return the opposite
        # results : False if so, otherwise True
        return not self._is_alien_link(link)
    
    def _get_articles(self):
        """
        Get all the article elements avaialable in the current
        page.

        """
        # Article elements class names
        a_class_names = 'DT5BTM w8MdNG cYylcv _1FGXgy _75qWlu iOzucJ JT3_zV vut4p9'
        # Links elements class names
        l_class_names = '_LM JT3_zV CKDt_l CKDt_l LyRfpJ'
        # Articles
        articles = self._sa._get_elements_by_class(a_class_names)
        # Filter articles with alien links
        valid_articles = []
        for article in articles:
            link = self._sa._get_element_by_class(l_class_names, article).get_attribute('href')
            if self._is_an_article_link(link):
                valid_articles.append(article)
        # Return only valid articles
        return valid_articles
    
    def _scrape_single_article(self, link: str):
        """
        Scrape a single article using a link.
        
        """
        # Validate the link
        if not self._is_an_article_link(link):
            self._sa.logger.log("The article's link is not valid.", 'WARNING')
            return "Not an article"
        # Get the article page
        self._sa.driver.get(link)
        # Define the article scrapper
        article_scrapper = ArticleScrapper(self._sa)
        # Scrape the article
        return article_scrapper.scrape()

    
    def _scrape_single_page(self, n_articles):
        """
        Get `n_articles` from the current page (page number `page_number`).

        """
        # Get the articles list
        articles_elements = self._get_articles()
        # Inform the number of found articles.
        self._sa.logger.log("Found {} articles."
                            "".format(len(articles_elements)), 'INFO')
        # Initiate the page articles with an empty dictionary.
        articles_details = {}
        # Extract the details of each found article
        for article_number, article in enumerate(articles_elements, start=1):
            # Initiate the article's details dictionary.
            article_details = {}
            # Open the artice details in a new tab
            try:
                with ArticleScrapper(self._sa, article) as article_scrapper:
                    # Scrape the article details.
                    _details = article_scrapper.scrape()
                    # Append the scrapped article's details and link
                    article_details.update(_details)
            except:
                self._sa.logger.log(traceback.format_exc(), 'ERROR', _br=True)
            # Append the scrapped articles to the pages'.
            articles_details.update({article_number : article_details})
            # Check if the maximum articles to scrape is reached.
            if article_number == n_articles:
                break
        # Inform the number of scrapped articles.
        self._sa.logger.log("Succefully {} articles were scrapped."
                            "".format(len(articles_details)), 'INFO')
        # Return the final results
        return articles_details


    def _scrape(self, n_articles, page_number=1):
        """
        Scrape the website.
        """
        # Inform starting scrapping the articles.
        self._sa.logger.log("Starting scrapping page  {} ... Link : {}"
                            "".format(page_number, self._curr_url()), 'INFO', _br=True)
        # Get the page's articles
        page_articles = self._scrape_single_page(n_articles)
        # Inform the succes of the  n_articles.
        self._sa.logger.log("{} articles scrapped successfully from page {}"
                            "".format(n_articles, page_number), 'INFO', _br=True)
        # Append the scrapped page to the scrapped data.
        self.scrapped_data.update({page_number: page_articles})

    def _start(self, n_pages=1, n_articles=1):
        """
        Start the process to scrape the first n_articles in each
        pages of the first n_pages.

        """
        # Get the targeted link (self.main_link)
        self._sa.driver.get(self.main_link)
        # handle cookies
        self._handle_cookies()
        # Search for the total items and pages
        self._save_page_details()
        # Start scrapping
        scrapped_pages = 0
        while True:
            # Scrape page articles.
            self._scrape(n_articles, scrapped_pages + 1)
            # Increase the number of scrapped pages.
            scrapped_pages += 1
            # Check if the maximum number of pages to scrape is
            # reached, or if there is not more pages to scrape.
            if scrapped_pages == n_pages or not self._next_page():
                # If so end the scrapping.
                break

    def scrape_articles(self, links: list[str] | str):
        """
        Scrape a single or a list of articles independently
        using their customized link.
        
        """
        # Make sure the links is alist.
        if not isinstance(links, list):
            links = [links]
        # handle cookies
        self._handle_cookies(get_link=True)
        # Initiate the details diction to holde the results
        articles_details = {}
        for article_number, article_link in enumerate(links, start=1):
            article_details = self._scrape_single_article(article_link)
            articles_details.update({article_number: article_details})
        # Return the articles' details
        return articles_details

    def scrape(self, n_pages=1, n_articles=1):
        """
        Start the process to scrape the first n_articles in each
        pages of the first n_pages.

        """
        try:
            self._start(n_pages, n_articles)
        except:
            self._sa.logger.log(traceback.format_exc(), 'ERROR', _br=True)
            self._sa.logger.log("Scrapping failed.", 'ERROR', _br=True)

    def save_metadata(self, meta_dict: dict):
        """
        Save the metadata to trace the last status of the scrapper.

        This must be helpful to continue the scrapping in case of
        any incident.

        """
        for key, value in meta_dict.items():
            self._metadata.update({key: value})
            # Log the added metadata
            self._sa.logger.log("{} = {} saved to metadata"
                                "".format(key, value), 'INFO')

    def to_dict(self, output_dir):
        """
        Save scrapped data and it's metadata into a json file, and
        return a dictionary.
        
        """
        # Save metadata
        with open(f"{output_dir}\\metadata.json", "w+", encoding='utf-8') as mf:
            json.dump(self._metadata, mf, indent=3, ensure_ascii=False)
        # Save the scrapperd data
        with open(f"{output_dir}\\output_data.json", "w+", encoding='utf-8') as mf:
            json.dump(self.scrapped_data, mf, indent=3, ensure_ascii=False)
        # Return the scrapped data
        return self.scrapped_data

    def to_pandas(self, read_json=False,
                  save_to_csv=True,
                  output_dir=None):
        """
        Convert the scrapped data into a pandas dataframe.
        
        """
        ...
