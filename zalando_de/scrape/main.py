import traceback

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import (TimeoutException,
                                        NoSuchWindowException,
                                        WebDriverException)

import json

from zalando_de.utils.helpers import (total_items,
                                      total_pages,
                                      current_datetime,
                                      delta_datetime,
                                      suffix_timer,
                                      is_a_directory)
from zalando_de.scrape.commun.assistants import ScraperAssistant
from zalando_de.scrape.units.article import ArticleScraper


BROWSER_CLOSED_EXCEPTIONS = (NoSuchWindowException,
                             WebDriverException,
                             ConnectionResetError)


ALIEN_LINKS = ['/outfits/', '/collections/', '/men/', '/campaigns/']


class Scraper():

    def __init__(self, assistant, out) -> None:
        # Logging configuration.
        self._sa: ScraperAssistant = self.__validate_assistant(assistant)
        # Define the outputs destination directory.
        self._output_directory = self.__validate_output_dir(out)
        # Log the initiation of the scraper
        self._sa.logger.info("Initiate the scraper object.", _br=True)
        # Main link
        self.main_link = "https://en.zalando.de/mens-clothing-shirts/"
        # Scraped data
        self.scraped_data = {}
        # Metadata
        self._metadata = {}
        # Scraped articles
        self.scraped_articles = self._read_scraped_articles()

    # NOTE: This needs to be improved.
    def __validate_assistant(self, assistant):
        if not assistant:
            raise ValueError("Invalid scraper assistant")
        return assistant
    
    # NOTE: This needs to be improved.
    def __validate_output_dir(self, out):
        if not is_a_directory(out):
            raise ValueError("Invalid output destination : {}"
                             "".format(out))
        return out
    
    def _save_metadata(self, meta_dict: dict):
        """
        Save the metadata to trace the last status of the scraper.

        This must be helpful to continue the scrapping in case of
        any incident.

        """
        for key, value in meta_dict.items():
            self._metadata.update({key: value})
            
    def _read_scraped_articles(self):
        """
        Read the already scraped articles.
        
        """
        try:
            input_fn = f"{self._output_directory}/scraped_articles.json"
            with open(input_fn, 'r+', encoding='utf-8') as input_file:
                scraped_articles = json.load(input_file)
            # Log
            self._sa.logger.info("Scraped articles are read : {} "
                                "articles.".format(len(scraped_articles)))
            return set(scraped_articles)
        
        except:
            return set()
            
    def _extract_id_from_link(self, link: str):
        """
        Extract an id for an article from its link.

        """
        article_id = (link.replace('https://en.zalando.de/', '')
                          .replace('.html', ''))
        return article_id
    
    def _save_article(self, article_id):
        """
        Save scraped articles.

        The purpose of saving the scraped articles is to avoid
        scrapping them twice.

        Articles are identifed by an ID extracted
        directly from their link.

        """
        # Save the article as successfully scraped.
        self.scraped_articles.add(article_id)

    def _save_scraped_articles(self):
        """
        Save the scraped article to json file.
        
        """
        # Prepare the articles to save.
        scraped_articles = list(self.scraped_articles)
        # Prepare the destination file name.
        output_fn = f"{self._output_directory}/scraped_articles.json"
        with open(output_fn, 'w+', encoding='utf-8') as output_file:
            json.dump(scraped_articles,
                      output_file,
                      indent=3,
                      ensure_ascii=False)
        # Log
        self._sa.logger.info("Scraped articles ({}) are saved to {}"
                             "".format(len(scraped_articles), output_fn))
        
    def _save_scraped_details(self):
        """
        Save scraped data and it's metadata into a json file.
        
        """
        # Prepare the dictionary to hold all the results.
        scraped_data = {'metadata': self._metadata,
                        'data': self.scraped_data}
        # Prepare the destination json file name
        output_fn = f"{self._output_directory}/scraped_details_{suffix_timer()}.json"
        # Save the scraperd data
        with open(output_fn, "w+", encoding='utf-8') as outpu_file:
            json.dump(scraped_data,
                      outpu_file,
                      indent=3,
                      ensure_ascii=False)
        # Log
        self._sa.logger.info("Scraped articles's details ({}) saved into {}"
                             "".format(len(self.scraped_data), output_fn))

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

    def _save_details(self):
        """
        Get the current page's details, and save them to metadata.
        
        Intended to be called only when the driver is on the
        main page.

        """
        # Total items
        class_names = '_0Qm8W1 _7Cm1F9 FxZV-M weHhRC u-6V88 FxZV-M'
        _total_items = total_items(self._sa._get_element_value_by_class(class_names))
        # Total pages
        class_names = '_0Qm8W1 _7Cm1F9 FxZV-M pVrzNP JCuRr_ _0xLoFW uEg2FS FCIprz'
        _, _total_pages = total_pages(self._sa._get_element_value_by_class(class_names))
        # Save the values into the scraper's metadata
        self._save_metadata({'total_pages': _total_pages,
                             'total_items': _total_items})
        # Return the details
        return _total_items, _total_pages
    
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
    
    def _is_valid_article(self, link: str):
        """
        Verify if the the actual opened page is for an article.
        
        """
        # Verify if the link is alien, and return the opposite
        # results : False if so, otherwise True
        if self._is_alien_link(link):
            return False
        # Verify if the article is already scraped or not
        _id = self._extract_id_from_link(link)
        if _id in self.scraped_articles:
            return False
        # Return the True (at this point the article is valid to scrape)
        return True
    
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
            if self._is_valid_article(link):
                valid_articles.append(article)
        # Return only valid articles
        return valid_articles
    
    def _scrape_single_article(self, link: str):
        """
        Scrape a single article using a link.
        
        """
        # Validate the link
        if not self._is_valid_article(link):
            self._sa.logger.warn("The article's link is not valid.")
            return "Not an article"
        # Get the article page
        self._sa.driver.get(link)
        # Define the article scraper
        article_scraper = ArticleScraper(self._sa)
        # Scrape the article
        return article_scraper.scrape()

    def _scrape_single_page(self):
        """
        Get all articles from the current page.

        """
        # Get the articles list
        articles_elements = self._get_articles()
        # Inform the number of found articles.
        self._sa.logger.info("Found {} articles."
                             "".format(len(articles_elements)))
        # Initiate the page articles with an empty dictionary.
        articles_details = {}
        # Extract the details of each found article
        for article in articles_elements:
            # Open the article details in a new tab
            try:
                with ArticleScraper(self._sa, article) as article_scraper:
                    # Scrape the article details.
                    article_details, article_id = article_scraper.scrape()
                    # Append the scraped article's details and link
                    self._save_article(article_id)
                    # Append the scraped articles to the pages'.
                    articles_details.update({article_id : article_details})
            # If the the browser windows forced to close (i.e. a
            # `NoSuchWindowException` or WebDriverException raised)
            # stop the process.
            except BROWSER_CLOSED_EXCEPTIONS as e:
                # Return the final results
                self.scraped_data.update(articles_details)
                # Inform the number of scraped articles.
                self._sa.logger.info("{} out of {} articles were succefully scraped."
                                    "".format(len(articles_details), len(articles_elements)),
                                    _br=True)
                raise e
            # If any other exception raise, log the exception trace,
            # and continue.
            except:
                self._sa.logger.error(traceback.format_exc(),
                                      show_details=False, _br=True)
        # Inform the number of scraped articles.
        self._sa.logger.info("{} out of {} articles were succefully scraped."
                            "".format(len(articles_details), len(articles_elements)),
                            _br=True)
        # Add the scraped data
        self.scraped_data.update(articles_details)

    def _scrape(self):
        """
        Start scrapping.

        """
        # Get the targeted link (self.main_link)
        self._sa.driver.get(self.main_link)
        # handle cookies
        self._handle_cookies()
        # Search for the total items and pages
        self._save_details()
        # Start scrapping
        while True:
            # Scrape page articles.
            self._sa.logger.info("Starting scrapping ...", _br=True)
            # Scrape the page's articles
            try:
                self._scrape_single_page()
            except Exception as e: raise e
            # If there is not more pages to scrape, stop.
            if not self._next_page():
                break

    def scrape(self):
        """
        Start the process of scrapping the men's shirts.

        """
        # Save the starting datetime.
        start_time, start_time_str = current_datetime()
        self._save_metadata({'started_at': start_time_str})
        try:
            self._scrape()
        # If the the browser windows forced to close (i.e. a
        # `NoSuchWindowException` or WebDriverException raised)
        # stop the process.
        except BROWSER_CLOSED_EXCEPTIONS:
                # Log the error
                self._sa.logger.error(traceback.format_exc(),
                                    show_details=False, _br=True)
                self._sa.logger.error("Failed to continue. It seems that the "
                                      "browser is forcefully closed.\n", _br=True)
        # If any other exception raise, log the exception trace,
        # and continue.
        except:
            self._sa.logger.error(traceback.format_exc(),
                                  show_details=False, _br=True)
            self._sa.logger.error("Scrapping failed.", _br=True)
        # Save the finishing datetime
        end_time, end_time_str = current_datetime()
        self._save_metadata({'finished_at': end_time_str,
                            'done_in': delta_datetime(start_time, end_time)})
        
    def scrape_articles(self, links: str):
        """
        Scrape a single or a list of articles independently
        using their customized link.
        
        This method is intended to be used only in case a set
        of articles are not perfectly scraped or were skipped
        while scrapping.

        """
        # Make sure the links is alist.
        if not isinstance(links, list):
            links = [links]
        # handle cookies
        self._handle_cookies(get_link=True)
        # Initiate the details diction to holde the results
        articles_details = {}
        for article_link in links:
            try:
                article_details, article_id = self._scrape_single_article(article_link)
                articles_details.update({article_id: article_details})
            # If the the browser windows forced to close (i.e. a
            # `NoSuchWindowException` or WebDriverException raised)
            # stop the process.
            except BROWSER_CLOSED_EXCEPTIONS:
                # Log the error
                self._sa.logger.error(traceback.format_exc(),
                                    show_details=False, _br=True)
                self._sa.logger.error("Failed to continue. It seems that the "
                                      "browser is forcefully closed.\n", _br=True)
                break
            # If any other exception raise, log the exception trace,
            # and continue.
            except:
                self._sa.logger.error(traceback.format_exc(),
                                    show_details=False, _br=True)
                self._sa.logger.error("The article Skipped : Failed to scrape.\n", _br=True)
        # Inform the number of scraped articles.
        self._sa.logger.info("{} out of {} articles were succefully scraped."
                            "".format(len(articles_details), len(links)),
                            _br=True)
        # Return the articles' details
        return articles_details

    def save_to_json(self):
        """
        Save scraped details and it's metadata into a json file.
        
        """
        # Log
        self._sa.logger.debug("Saving the scraped articles ...")
        self._save_scraped_details()
        self._save_scraped_articles()
        # Log the success of saving the data.
        self._sa.logger.info("Done.")

    def _clean_scraped_articles(self):
        """
        _clean_scraped_articles
        
        """
        _data = self.scraped_data


    def save_to_csv(self):
        """
        Read all the scraped articles from json files, convert it
        into a pandas dataframe, and save it as csv.
        
        """
        dataframe = self._clean_scraped_articles()
