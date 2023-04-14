from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import (TimeoutException,
                                        WebDriverException,
                                        NoSuchWindowException,
                                        StaleElementReferenceException)

# from urllib3.exceptions import HTTPError

import json
import pandas as pd

from zalando_de.utils.helpers import *
from zalando_de.scrape.commun.exceptions import *
from zalando_de.scrape.commun.assistants import ScraperAssistant
from zalando_de.scrape.commun.cleaners import Cleaner
from zalando_de.scrape.units.article import ArticleScraper


ALIEN_LINKS = ['/outfits/', '/collections/', '/men/', '/campaigns/', '/mens-clothing/']

ID_COLNAME = 'ID'

# BClosedExceptions = (NoSuchWindowException,
#                      StaleElementReferenceException,
#                      HTTPError,
#                      ConnectionError)


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
        self._csv_sep = ","
        self._processed_articles = self._get_processed_articles()
        self._newl_processed_articles = {}
        self._skipped_articles = {}
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
            prev_processed_articles = set(pd.read_csv(articles_path,
                                                      sep=self._csv_sep,
                                                      encoding='utf-8')[ID_COLNAME])
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
                prev_metas = {}
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
    
    def _skip_article(self, id, reason_to_skip_for):
        """
        Add the skipped article to self._skipped_articles.
        
        """
        self._skipped_articles.update({id: reason_to_skip_for})
        if 'skipped_articles' in self._metadata:
            self._metadata['skipped_articles'] += 1
        else: self._add_metadata({'skipped_articles': 1})

    def _save_article(self, id, details):
        """
        Add the processed article to self._newl_processed_articles
        and self._processed_articles.
        
        """
        self._newl_processed_articles.update({id: details})
        self._processed_articles.add(id)
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
    
    def _get_article_link(self, article_element: WebElement):
        """
        Find the article's url.
        
        """
        class_names = '_LM JT3_zV CKDt_l CKDt_l LyRfpJ'
        link = self._sa._get_element_by_class(class_names,
                                              article_element).get_attribute('href')
        return link
    
    def _is_alien_link(self, link: str):
        """
        Verify if a link is alien or not.
        
        """
        # Ensure the link ends with .html
        if not link.endswith(".html"):
            return True
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
        _id = self._extract_ID(link)
        # Verify if the link is alien, and return the opposite
        # results : False if so, otherwise True
        if self._is_alien_link(link) or "/" in _id:
            return False, "an alien link"
        # Verify if the article is already scraped or not
        if _id in self._processed_articles:
            return False, "already processed"
        # Return the True (at this point the article is valid to scrape)
        return True, "ok"
    
    def _get_page_articles(self):
        """
        Get all the article elements avaialable in the current
        page.

        """
        self._sa.logger.info("Searching page's articles ...",
                             _lbr=True, _rbr=True)
        # Article elements class names
        class_names = 'DT5BTM w8MdNG cYylcv _1FGXgy _75qWlu iOzucJ JT3_zV vut4p9'
        # Articles
        articles = self._sa._get_elements_by_class(class_names)
        # Filter articles with alien links
        valid_articles, duplicated = [], 0
        for article in articles:
            try:
                link = self._get_article_link(article)
            except StaleElementReferenceException as se_e:
                self._sa.logger.debu0("Staled element skipped.")
                continue
            # Validate the article (using the link)
            is_valid, valid_msg = self._is_valid_article(link)
            if is_valid:
                valid_articles.append((article, link))
            else:
                self._sa.logger.info("The article ( {} ) is {}."
                                     "".format(link, valid_msg))
            if valid_msg == 'already processed':
                duplicated += 1
        # Return only valid articles
        return valid_articles, duplicated
    
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
    
    def _save_to_json_skipped_articles(self):
        """
        Save skipped articles into a json file.
        
        """
        # Prepare the destination json file name
        # NOTE : As all the skipped articles in the previous runs will be
        # re-processed again in next's, the previously saved skipped articles
        # can be overwrited with no proble.
        json_fn = f"{self._output_directory}/skipped_shirts.json"
        # Save the articles
        with open(json_fn, "w+", encoding='utf-8') as output_file:
            json.dump(self._skipped_articles,
                      output_file,
                      indent=3,
                      ensure_ascii=False)
        return norm_path(json_fn)

    def _save_to_json(self):
        """
        Save processed articles into a json file.
        
        """
        # Prepare the destination json file name
        json_fn = f"{self._output_directory}/{self._output_filename}(uncleaned).json"
        # Prepare the dictionary to hold all the results.
        processed_articles = {suffix_timer():{'metadata': self._metadata,
                                              'data': self._newl_processed_articles}}
        
        try:
            with open(json_fn, "r+", encoding='utf-8') as output_file:
                prev_processed_articles = json.load(output_file)
        except Exception:
            prev_processed_articles = {}
        # Update the read file
        prev_processed_articles.update(processed_articles)
        # Save the scraperd data
        with open(json_fn, "w+", encoding='utf-8') as output_file:
            json.dump(prev_processed_articles,
                      output_file,
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
            prev_processed_articles = pd.read_csv(csv_fn,
                                                  sep=self._csv_sep,
                                                  encoding='utf-8')
        except FileNotFoundError:
            prev_processed_articles = None
        # Save the dataframe into a CSV file.
        (pd.concat([prev_processed_articles,
                    newl_processed_articles])
           .to_csv(path_or_buf=csv_fn,
                   index=False,
                   sep=self._csv_sep,
                   encoding='utf-8'))
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
        saved_to = self._save_to_json_skipped_articles()
        self._sa.logger.info("Un-processed articles saved (JSON) into {}"
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
        articles_elements, n_duplicated = self._get_page_articles()
        n_valid_articles = len(articles_elements)
        n_articles = n_valid_articles + n_duplicated
        # Inform the number of found articles.
        self._sa.logger.info("Found {} articles (out of {}) to process "
                             "[{} were processed in previous pages]."
                             "".format(n_valid_articles, n_articles, n_duplicated))
        # Initiate the page articles with an empty dictionary.
        try:        
            successive_skips, internet_issue = 0, False
            processed_articles = 0
            # Extract the details of each found article
            for (article, link) in articles_elements:
                # Extract the article ID
                article_id = self._extract_ID(link)
                # Open the article details in a new tab
                # NOTE : The new tab must be closed by quiting this
                # `with` statement.
                with ArticleScraper(self._sa, article) as article_scraper:
                    # Process the article to scrape the details.
                    try:
                        article_details = article_scraper.scrape(link)
                        # Add the link to article's details.
                        article_details.update({'url': link,
                                                'scraped_in': timer()})
                        # Append the processed article to the pages', in case
                        # no error occured and no exception raised.
                        self._save_article(article_id, article_details)
                        processed_articles += 1
                    # In case processing the article failed, then an
                    # `ArticleProcessingException` must been raised.
                    except ArticleProcessingException as ap_e:
                    # If the processing exception is a timeout's,
                    # skip the article and continue.
                        if isinstance(ap_e.exc_error, TimeoutException):
                            # Append the skipped article to the pages', in case
                            # a TimeoutException exception raised.
                            self._skip_article(article_id, 'TimeoutException')
                            successive_skips += 1
                            # If the TimeoutException is catched more than 3 time
                            # successively, then probably there is an Internet
                            # connection issue. Hence break the loop and raise
                            # an UnableToConnectException exception after the
                            # exiting the ArticleScraper context manager.
                            if successive_skips > 2:
                                internet_issue = True
                                break
                            # If not, continue.
                            continue
                        successive_skips = 0
                        raise ap_e
            # If internet issue is True, the TimeoutException was catched more
            # than 3 time successively.
            if internet_issue:
                exc_message = "Probably the Internet connection is unstable."
                raise UnableToConnectException(exc_message,
                                               TimeoutException(),
                                               self._sa.logger).dbg()
        # Inform the number of scraped articles.
        finally:
            self._sa.logger.info("{} out of {} articles were successfully "
                                 "processed.".format(processed_articles,
                                                     len(articles_elements)),
                                 _lbr=True, _rbr=True)

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
            # Process the page's articles
            self._sa.logger.info("Processing new page "
                                 "{}".format('='*49),
                                 _lbr=True, _rbr=True)
            try:
                self._process_page()
                # If there is not more pages to scrape, stop.
                if not self._is_next_page(): break
            except BaseException as be:
                raise be
    
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
        successive_skips, internet_issue = 0, False
        try:
            for article_link in links:
                self._sa.logger.log("", show_details=False)
                # Get the article ID
                article_id = self._extract_ID(article_link)
                # Validate the link
                is_valid, valid_msg = self._is_valid_article(article_link)
                if not is_valid:
                    self._sa.logger.info("The article ( {} ) is {}."
                                     "".format(article_link, valid_msg))
                    continue
                # Get the article page
                self._sa.get(article_link)
                # Process the article to scrape the details.
                try:
                    article_details = article_scraper.scrape(article_link)
                    # Add the link to article's details.
                    article_details.update({'url': article_link,
                                            'scraped_in': timer()})
                    # Append the processed article to the pages', in case
                    # no error occured and no exception raised.
                    self._save_article(article_id, article_details)
                # In case processing the article failed, then an
                # `ArticleProcessingException` must been raised.
                except ArticleProcessingException as ap_e:
                    # If the processing exception is a timeout's,
                    # skip the article and continue.
                        if isinstance(ap_e.exc_error, TimeoutException):
                            # Append the skipped article to the pages', in case
                            # a TimeoutException exception raised.
                            self._skip_article(article_id, 'TimeoutException')
                            successive_skips += 1
                            # If the TimeoutException is catched more than 3 time
                            # successively, then probably there is an Internet
                            # connection issue. Hence break the loop and raise
                            # an UnableToConnectException exception after the
                            # exiting the ArticleScraper context manager.
                            if successive_skips > 2:
                                internet_issue = True
                                break
                            # If not, continue.
                            continue
                        successive_skips = 0
                        raise ap_e
            # If internet issue is True, the TimeoutException was catched more
            # than 3 time successively.
            if internet_issue:
                exc_message = "Probably the Internet connection is unstable."
                raise UnableToConnectException(exc_message,
                                               TimeoutException(),
                                               self._sa.logger).dbg()
        finally:
            # Inform the number of scraped articles.
            self._sa.logger.info("{} out of {} articles were successfully scraped."
                                "".format(len(self._newl_processed_articles),
                                          len(links)), _lbr=True)

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
        # If the the exception is a KeyboardInterrupt, and it's already
        # handled raise the `KeyboardInterruptException` raised then.
        except KeyboardInterruptException as ki_e:
            raise ki_e
        # If the the exception is a KeyboardInterrupt raise
        # `KeyboardInterruptException`.
        except KeyboardInterrupt as ki_e:
            exc_message = "Processing forcibly stopped using CTR + C."
            raise KeyboardInterruptException(exc_message, ki_e,
                                             self._sa.logger).dbg()
        # If the exception is alredy handled, and it was related to an 
        # internet connection issue, raise it.
        except UnableToConnectException as uc_e:
            raise uc_e
        # If the exception is already handled, and it's raised in the
        # article's page, raise `WindowAlreadyClosedException`.
        except (UnableToOpenNewTabException,
                ArticleProcessingException,
                UnableToCloseNewTabException) as exc:
            exc_message = "Probably the browser is been forcibly closed."
            raise WindowAlreadyClosedException(exc_message, exc,
                                                self._sa.logger).dbg()
        # If it's a WebDriverException exception, handle all the cases
        except WebDriverException as wd_e:
            # It's exactly a NoSuchWindowException, the raise
            # `WindowAlreadyClosedException`
            if isinstance(wd_e, NoSuchWindowException):
                exc_message = "Probably the browser is been forcibly closed."
                raise WindowAlreadyClosedException(exc_message, wd_e,
                                                   self._sa.logger).dbg()
            # If the reason the exception raised is the
            # internet connection (Any issue identified as internet related.)
            elif  _is_internet_related(wd_e.msg) or isinstance(wd_e, TimeoutException):
                exc_message = "Probably the Internet connection is unstable."
                raise UnableToConnectException(exc_message,
                                               exc, self._sa.logger).dbg()
            # Otherwise, raise `ArticlesProcessingException`
            exc_message = ("An unexpected Web Driver Exception "
                           "raised. Probably due to forcibly close "
                           "the browser.")
            raise ArticlesProcessingException(exc_message, wd_e,
                                              self._sa.logger)
        finally:
            # Save the finishing datetime
            end_time, end_time_str = current_datetime()
            self._add_metadata({'finished_at': end_time_str,
                                'done_in': delta_datetime(start_time, end_time)})
            self._sa.logger.info("Saving processed articles' data ...",
                                 _lbr=True, _rbr=True)
            self._save()


def _is_internet_related(msg):
    """
    """
    MSG_INET = ["err_internet_disconnected",
                "err_connection_timed_out",
                "err_name_not_resolved"]
    
    for i_msg in MSG_INET:
        if i_msg in msg.lower():
            return True
    return False