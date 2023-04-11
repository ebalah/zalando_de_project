import traceback

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import (TimeoutException,
                                        NoSuchWindowException,
                                        WebDriverException)

import json
import pandas as pd

from zalando_de.utils.helpers import (total_items, total_pages, norm_path,
                                      current_datetime, delta_datetime,
                                      suffix_timer, is_a_directory)
from zalando_de.scrape.commun.assistants import ScraperAssistant
from zalando_de.scrape.commun.cleaners import Cleaner
from zalando_de.scrape.units.article import ArticleScraper


BROWSER_CLOSED_EXCEPTIONS = (NoSuchWindowException,
                             WebDriverException,
                             ConnectionResetError)


ALIEN_LINKS = ['/outfits/', '/collections/', '/men/', '/campaigns/']

ID_COLNAME = 'ID'


class Scraper():

    def __init__(self, assistant, out) -> None:
        # Logging configuration.
        self._sa: ScraperAssistant = self.__validate_assistant(assistant)
        # Define the outputs destination directory and name.
        self._output_directory = self.__validate_output_dir(out)
        self._output_filename = "zalando_de_mens_shirts"
        # Define the 
        # Log the initiation of the scraper
        self._sa.logger.info("Initiate the scraper object.", _lbr=True)
        # Main link
        self._main_link = "https://en.zalando.de/mens-clothing-shirts/"
        # ...
        self._cleaner = Cleaner()
        self._csv_sep = "|"
        self._prev_processed_articles = self._get_processed_articles()
        self._newl_processed_articles = {}
        self._metadata = {}

    def __validate_assistant(self, assistant):
        if not assistant:
            raise ValueError("Invalid scraper assistant.")
        return assistant
    
    def __validate_output_dir(self, out):
        if not is_a_directory(out):
            raise ValueError("Invalid output destination : {}"
                             "".format(out))
        return out

    def _handle_cookies(self, accept=False,
                        get_link: bool = False):
        """
        Accept cookies popup.
        
        """
        # If get_link, then get the driver to the main link
        if get_link:
            self._sa.get(self._main_link)

        # Wait for the dialog presence.
        try:
            self._sa.xlong_wait.until(ec.visibility_of_element_located((By.ID,
                                                                        'uc-main-banner')),
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
            
    def _get_processed_articles(self):
        """
        Read the previously processed articles.
        
        """
        articles_path = f"{self._output_directory}/{self._output_filename}.csv"
        try:
            prev_processed_articles = set(pd.read_csv(articles_path, sep=self._csv_sep)[ID_COLNAME])
            self._sa.logger.info("Processed articles read : {} "
                                "articles.".format(prev_processed_articles.__len__()))
        except FileNotFoundError:
            prev_processed_articles = set()
        return prev_processed_articles
    
    def _add_metadata(self, meta_dict: dict):
        """
        Add to metadata to trace the last status of the scraper.

        This must be helpful to continue the processing in case of
        any incident.

        """
        for key, value in meta_dict.items():
            self._metadata.update({key: value})

    def _save_metadata(self):
        """
        Save the metadata to trace the last status of the scraper.

        This must be helpful to continue the processing in case of
        any incident.

        """
        metadata_path = f"{self._output_directory}/metadata.json"
        meta_dict = {suffix_timer(): self._metadata}
        # Read the old metadata file's content.
        try:
            with open(metadata_path, 'r+', encoding='utf-8') as mf:
                prev_metas = json.load(mf)
        except Exception as e:
            if (isinstance(e, FileNotFoundError) or
                (isinstance(e, json.JSONDecodeError) 
                    and e.msg == "Expecting value")):
                prev_metas = {}
            else : raise
        meta_dict.update(prev_metas)
        # Update the metadata file's content.
        with open(metadata_path, 'w+', encoding='utf-8') as mf:
            json.dump(meta_dict,
                      mf, indent=3,
                      ensure_ascii=False)
        # Return the path the metadata saved to
        return norm_path(metadata_path)
            
    def _extract_ID(self, link: str):
        """
        Extract an id for an article from its link.

        """
        article_id = (link.replace('https://en.zalando.de/', '')
                          .replace('.html', ''))
        return article_id

    def _save_article(self, id, details):
        """
        Save the scraped article to csv file.
        
        """
        self._newl_processed_articles.update({id: details})
        if 'processed_articles' in self._metadata:
            self._metadata['processed_articles'] += 1
        else: self._add_metadata({'processed_articles': 1})

    def _high_level_details(self):
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
        self._add_metadata({'total_pages': _total_pages,
                             'total_items': _total_items})
        # Return the details
        return _total_items, _total_pages
    
    def _get_current_url(self):
        """
        Get the currently opened page's url.

        """
        return self._sa.driver.current_url

    def _is_next_page(self):
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
        _id = self._extract_ID(link)
        if _id in self._prev_processed_articles:
            return False
        # Return the True (at this point the article is valid to scrape)
        return True
    
    def _get_page_articles(self):
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
    
    def _clean_processed_articles(self):
        """
        _clean_processed_articles
        
        """
        # Newly processed articles
        processed_articles = self._newl_processed_articles
        # Clean the processed articles' details.
        # NOTE: This cleaning is needed to clean the price and
        # split the data entries of :
        # - Material & care,
        # - Size & Fit,
        # - and Details.
        for _id, _details in processed_articles.items():
            cleaned = self._cleaner.clean(_details)
            processed_articles.update({_id: cleaned})
        # Create a new datarame of the cleaned data.
        return pd.DataFrame.from_dict(processed_articles,
                                      orient="index").reset_index(drop=False,
                                                                  names=['ID'])
    
    def _save_to_json(self):
        """
        Save processed articles into a json file.
        
        """
        # Prepare the dictionary to hold all the results.
        processed_articles = {'metadata': self._metadata,
                              'data': self._newl_processed_articles}
        # Prepare the destination json file name
        json_fn = f"{self._output_directory}/{self._output_filename}__{suffix_timer()}.json"
        # Save the scraperd data
        with open(json_fn, "w+", encoding='utf-8') as outpu_file:
            json.dump(processed_articles,
                      outpu_file,
                      indent=3,
                      ensure_ascii=False)
        # Return the path the data saved to
        return norm_path(json_fn)
            
    def _save_to_csv(self):
        """
        Save processed articles into a csv file.
        
        """
        csv_fn = f"{self._output_directory}/{self._output_filename}.csv"
        # Convert the processed articles' details to a dataframe.
        newl_processed_articles = self._clean_processed_articles()
        # Read the previously processed articles CSV file.
        try:
            prev_processed_articles = pd.read_csv(csv_fn, sep=self._csv_sep)
        except FileNotFoundError:
            prev_processed_articles = None
        # Save the dataframe into a CSV file.
        pd.concat([prev_processed_articles,
                   newl_processed_articles]).to_csv(csv_fn,
                                                    index=False,
                                                    sep=self._csv_sep)
        # Return the path the data saved to
        return norm_path(csv_fn)

    def _save(self):
        """
        Save processed articles into a JSON and CSV files.

        Also a metadata json file is saved.
        
        """
        saved_to = self._save_metadata()
        self._sa.logger.info("Metadata saved into {}"
                             "".format(saved_to))
        saved_to = self._save_to_json()
        self._sa.logger.info("Processed articles saved (JSON) into {}"
                             "".format(saved_to))
        saved_to = self._save_to_csv()
        self._sa.logger.info("Processed articles saved (CSV) into {}"
                             "".format(saved_to))
        
    def _process_page(self):
        """
        Process all the articles in the current page.

        """
        # The list of all articles
        articles_elements = self._get_page_articles()
        # Inform the number of found articles.
        self._sa.logger.info("Found {} articles."
                             "".format(len(articles_elements)))
        processed_articles = 0
        # Initiate the page articles with an empty dictionary.
        try:
            # Extract the details of each found article
            for article in articles_elements:
                # Open the article details in a new tab
                try:
                    with ArticleScraper(self._sa, article) as article_scraper:
                        # Process the article to scrape the details.
                        article_details, article_id = article_scraper.scrape()
                        # Append the processed article to the pages'.
                        self._save_article(article_id, article_details)
                        # Inform the sucess of processing the article.
                        processed_articles += 1
                # If the the browser windows forced to close (i.e. a
                # `NoSuchWindowException` or WebDriverException raised)
                # stop the process.
                except BROWSER_CLOSED_EXCEPTIONS: raise
                # If any other exception is raised, log the trace and
                # continue.
                except Exception as e:
                    # Log the trace to show the skipping cause.
                    self._sa.logger.error(traceback.format_exc(),
                                        show_details=False, _lbr=True, _rbr=True)
                    self._sa.logger.warn("Processing Failed. Skipped.")
                    continue
        # If processing the article failed, log the trace to identify
        # the reason why.
        except Exception as e: raise e
        # Inform the number of scraped articles.
        finally:
            self._sa.logger.info("{} out of {} articles were succefully "
                                 "processed.".format(processed_articles,
                                                     len(articles_elements)),
                                _lbr=True)

    def _process(self):
        """
        Start processing.

        """
        # Get the targeted link (self._main_link)
        self._sa.get(self._main_link)
        # handle cookies
        self._handle_cookies()
        # Search for the total items and pages
        self._high_level_details()
        # Start processing
        while True:
            # Scrape page articles.
            self._sa.logger.info("Processing new page ...", _lbr=True)
            # Scrape the page's articles
            try:
                self._process_page()
                # If there is not more pages to scrape, stop.
                if not self._is_next_page(): break
            # ...
            except Exception: raise
    
    def _process_articles(self, links: str):
        """
        Scrape a single or a list of articles independently
        using their customized link.
        
        This method is intended to be used only in case a set
        of articles are not perfectly scraped or were skipped
        while processing.

        """
        # Make sure the links is alist.
        if not isinstance(links, list):
            links = [links]
        # handle cookies
        self._handle_cookies(get_link=True)
        # Define the article scraper
        article_scraper = ArticleScraper(self._sa)
        processed_articles = 0
        try:
            for article_link in links:
                # Get the article page
                self._sa.get(article_link)
                # Validate the link
                if not self._is_valid_article(article_link):
                    self._sa.logger.warn("The link ( {} ) is not for a valid"
                                        "article. Processing skipped."
                                        "".format(article_link))
                    continue
                try:
                    article_details, article_id = article_scraper.scrape()
                    self._save_article(article_id, article_details)
                    processed_articles += 1
                # If the the browser windows forced to close (i.e. a
                # `NoSuchWindowException` or WebDriverException raised)
                # stop the process.
                except BROWSER_CLOSED_EXCEPTIONS: raise
                # If any other exception is raised, log the trace and
                # continue.
                except Exception as e:
                    # Log the trace to show the skipping cause.
                    self._sa.logger.error(traceback.format_exc(),
                                        show_details=False, _lbr=True, _rbr=True)
                    self._sa.logger.warn("Processing Failed. Skipped.")
                    continue
        # If processing the article failed, log the trace to identify
        # the reason why.
        except Exception as e: raise e
        finally:
            # Inform the number of scraped articles.
            self._sa.logger.info("{} out of {} articles were succefully scraped."
                                "".format(processed_articles, len(links)),
                                _lbr=True)

    def scrape(self, how: str = 'all', links: list = []):
        """
        Start the process of processing the men's shirts.

        - If the how is set to `'all'`, links is ignored, and
        all the available articles will be processed.

        - If `'single'`, then only the articles whom link is
        specfied in `links` will be processed.

        """
        # Save the starting datetime.
        start_time, start_time_str = current_datetime()
        self._add_metadata({'started_at': start_time_str})
        
        # Pick the requested scraping method.
        if how == 'single':
            process_func = self._process_articles
            args = [links]
        else:
            process_func = self._process
            args = []

        try:
            process_func(*args)
        # If the the browser windows forced to close (i.e. a
        # `NoSuchWindowException` or WebDriverException raised)
        # stop the process.
        except Exception as e:
                # If the exception is raised because the browser was
                # forced to close (manualy), add an attricute to it
                # so it can be identifed later.
                if isinstance(e, BROWSER_CLOSED_EXCEPTIONS):
                    self._sa.logger.error("Failed to continue. It "
                                          "seems that the browser is "
                                          "forcibly closed.",
                                          _lbr=True, _rbr=True)
                    self._sa.logger.error(traceback.format_exc(),
                                          show_details=False)
                    e.reason_why = "BrowserClosedForcibly"
                else:
                    e.reason_why = ""
                raise e
        finally:
            # Save the finishing datetime
            end_time, end_time_str = current_datetime()
            self._add_metadata({'finished_at': end_time_str,
                                'done_in': delta_datetime(start_time, end_time)})
            self._save()

