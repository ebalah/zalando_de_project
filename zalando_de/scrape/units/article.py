import traceback

from selenium.webdriver.common.by import By
from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException,
                                        NoSuchWindowException,
                                        WebDriverException,
                                        TimeoutException)


from zalando_de.scrape.commun.assistants import ScraperAssistant
from zalando_de.scrape.commun.exceptions import (UnableToOpenNewTabException,
                                                 UnableToCloseNewTabException,
                                                 ArticleProcessingException)



class DeadScraperAssistantError(Exception):
    """
    An exception to handle browser closing errors,
    and validate the assistant.
    
    """


class ArticleScraper():

    """
    A context manager to manage articles in a new tab.
    
    """

    window_close_exc_msg = "no such window: target window already closed"
    browser_close_exc_msg = "disconnected: not connected to DevTools"

    def __init__(self, assistant,
                 article_element = None) -> None:
        self._sa: ScraperAssistant = self._validate_assistant(assistant)
        self._article_element = article_element

    def __enter__(self):
        # Open a new tab to handle the article.
        self._open_new_tab()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        # # In case of exiting with an error that was
        # # occured within the `with` block, raise it after
        # # making sure the new opened tab was closed.
        # if exc_type is not None:
        #     self._sa.logger.debug("The {} exited with an exception."
        #                           "".format(type(self).__name__),
        #                           _rbr=True)
        #     self._sa.logger.error("".join(traceback
        #                             .format_exception(exc_type,
        #                                               exc_value,
        #                                               tb)),
        #                           show_details=False)
        # # Close the opened tab and get back to the articles' page
        self._close_new_tab()
    
    def _open_new_tab(self):
        """
        Open a new Tab to process the targeted article.

        """
        try:
            self._sa._click_to_new_tab(self._article_element)
            self._sa.logger.debug("New article's Tab opened.", _lbr=True)
        except Exception as e:
            # If opening the new tab failed, then probably either :
            #
            #   - A `StaleElementReferenceException` was raised because the
            #     previous article's opened tab was not closed ( i.e. the
            #     article element is not available in the dom [stale] ).
            if isinstance(e, StaleElementReferenceException):
                exc_message = ("The article element is stale. "
                               "Probably the previous article's tab "
                               "was not closed.")
                exc_label = "prev_article_tab_not_closed_err"
            #   - A `NoSuchWindowException` exception was raised because the 
            #     the current window is already closed.
            # elif isinstance(e, NoSuchWindowException):
            #     exc_message = ("The current window was not found. "
            #                    "Probably the window forcibly closed.")
            #     exc_label = "current_window_already_closed_err"
            #   - A `NoSuchWindowException` exception was raised because the 
            #     the driver (browser) is forcibly closed.
            elif isinstance(e, WebDriverException):
                exc_message = ("An unexpected Web Driver Exception "
                               "raised. Probably due to forcibly closing "
                               "the browser.")
                exc_label = "browser_already_closed_err"
            #   - Or, an another exception.
            else :
                exc_message = "An unexpected Exception."
                exc_label = ""
            # Raise an UnableToOpenNewTabException exception
            raise UnableToOpenNewTabException(exc_message, exc_label, e)

    def _close_new_tab(self):
        """
        Close the new Tab opened to process the article.

        """
        try:
            self._sa._close_and_get_back()
            self._sa.logger.debug("Tab closed.")
        # If closing the new tabe failed, then it must be
        # because the window, or the browser is already closed
        # either forcibly by the user or after an unexpected
        # error occured.
        except BaseException as e:
            # Handle web driver exceptions
            if (isinstance(e, NoSuchWindowException) and
                    self.window_close_exc_msg in e.msg):
                exc_message = "Target window is already closed."
                exc_label = "current_window_already_closed_err"
            elif (isinstance(e, WebDriverException) and 
                    self.browser_close_exc_msg in e.msg):
                exc_message = "The browser is already closed."
                exc_label = "browser_already_closed_err"
            else:
                exc_message = "An unexpected Exception."
                exc_label = ""
            # Raise UnableToCloseNewTabException exception
            raise UnableToCloseNewTabException(exc_message, exc_label, e)

    def _validate_assistant(self, assistant):
        if not hasattr(assistant, 'driver'):
            raise DeadScraperAssistantError("Assistant object must have"
                                             "'driver' attrbute.")
        return assistant

    def _get_container(self):
        """
        Get the article's details container.
        
        """
        return self._sa._get_element_by_class('DT5BTM VHXqc_ rceRmQ _4NtqZU mIlIve')

    def _get_brand_name(self, _from = None):
        """
        Get the article brand.

        """
        # Class names for brand element.
        class_names = 'SZKKsK mt1kvu FxZV-M pVrzNP _5Yd-hZ'
        # Get the brand name
        return self._sa._get_element_value_by_class(class_names, _from)
    
    def _get_name(self, _from = None):
        """
        Get the article's name

        """
        class_names = 'EKabf7 R_QwOV'
        return self._sa._get_element_value_by_class(class_names, _from)
    
    def _get_price(self, _from = None):
        """
        Get the price label of the article.

        """
        class_names = '_0xLoFW _78xIQ-'
        price_label: str = self._sa._get_element_value_by_class(class_names, _from)
        return price_label.replace('\n', ' | ')

    def _get_colors(self, _from = None):
        """
        Get the list of all the available colors of the article.
        
        """
        # Get the element of color section
        # color_section = self._sa._get_element_by_class('SXSnE1 _8O8c-d')
        # Get displayed color.
        curr_displayed_color = self._sa._get_element_by_class('_0Qm8W1 u-6V88 dgII7d pVrzNP zN9KaA',
                                                              _from).text
        colors = []
        # get all colors items
        all_colors = self._sa._get_elements_by_class('pl0w2g DT5BTM A-NCMf', _from)
        # If no color was found in this section, return the currently
        # displayed color.
        if not all_colors:
            return [curr_displayed_color]
        # Iterate over all colors elements and get the alt
        # attribute of the img tag in each.
        for color_element in all_colors:
            # Search for the img tag and get the alt attribute.
            try:
                color_name = color_element.find_element(By.TAG_NAME, 'img').get_attribute('alt')
            except NoSuchElementException as e:
                continue
            # Append the color to colors.
            colors.append(color_name)
        # Return the found colors
        return colors
    
    def _get_sizes(self, _from = None):
        """
        Get the list all the available sizes of the article.
        
        """
        # Get the select-button used to select sizes
        size_picker = self._sa._get_element_by_id('picker-trigger')
        # and click it.
        self._sa._move_mouse_to_and_click(size_picker)
        # MH : sleep for 1 second
        self._sa._sleep_t_sec()
        # Get all sizes and their availability.
        sizes = {}
        # get all sizes
        all_sizes = self._sa._get_elements_by_class('fOd40J _0xLoFW JT3_zV FCIprz LyRfpJ')
        # Iterate over all sizes and extract the availability
        # and the label of each.
        for size_element in all_sizes:
            # Get availability label : can be "Notify Me", "Only x left", or ""
            availability_label = self._sa._get_element_value_by_class('nXkCf3', size_element)
            # NOTE: Sometimes the price depends on the size,
            # and therefor for each a specific price is shown.
            # Try to get the price if it's present for the current size.
            try: 
                price_label = self._sa._get_element_value_by_class('_0Qm8W1 u-6V88 FxZV-M pVrzNP ra-RRD',
                                                                   size_element)
            except:
                price_label = ""
            # get the size label
            class_names = ('_0Qm8W1 _7Cm1F9 dgII7d pVrzNP'
                           if availability_label != "Notify Me"
                           else '_0Qm8W1 _7Cm1F9 dgII7d D--idb')
            size_label = self._sa._get_element_value_by_class(class_names, size_element)
            # Append the size to sizes.
            sizes.update({size_label: {'count': availability_label,
                                       'price': price_label}})
        # Mimic human behavior
        self._sa.sleep_and_scroll()
        # Return the found sizes
        return sizes

    def _get_extra_details(self, _from = None):
        """
        Get the details entries of :
            
        - Fit & Size
        - Material & Care
        - Details
        
        """
        # Get the details elements.
        details_items = self._sa._get_elements_by_class('y4Yt_f NN8L-8 JT3_zV MxUWj-', _from)
        # Initiate the details dictionary to each detail with
        # its entries.
        details = {}
        # Iterate over the three elements, and get the name,
        # the keys, and the values of each.
        for item_element in details_items:
            # Get the name of item : must be one of :
            # - Fit & Size
            # - Material & Care
            # - Details
            item_name = self._sa._get_element_value_by_class('JCuRr_', item_element)
            # Get the key of each entry in details item
            item_keys = self._sa._get_elements_by_class('_0Qm8W1 u-6V88 dgII7d pVrzNP zN9KaA',
                                                    item_element)
            # Get the value of each entry in details item
            item_vals = self._sa._get_elements_by_class('_0Qm8W1 u-6V88 FxZV-M pVrzNP zN9KaA',
                                                    item_element)
            # Iterate over the keys and values and concatenate them in
            item_entries = {}
            # ... dictionary.
            for key, value in zip(item_keys, item_vals):
                item_entries.update({key.get_attribute('innerHTML')
                                        .replace(':', ''): value.get_attribute('innerHTML')})
            # Append the entries into details
            details.update({item_name: item_entries})
        # Mimic human behavior
        self._sa.sleep_and_scroll()
        # Finally, return the found deatils
        return details

    def _scrape(self, url: str = None):
        """
        Get all details of the article displayed in the current
        browser.
        
        `url` parameter is used only for logging.

        """
        # Inform the start of processing the article.
        st_msg = ("Processing new article started{}"
                  "".format(f" {url}" if url else "."))
        self._sa.logger.info(st_msg)
        # Get the article container.
        article_container = self._get_container()
        # Get the data in x-wrapper-re-1-4 container.
        x_wrapper_container = self._sa._get_element_by_tag_name('x-wrapper-re-1-4',
                                                                article_container)
        # The name of the brand
        brand_name = self._get_brand_name(_from=x_wrapper_container)
        self._sa.logger.debug('Brand name found : {}'.format(brand_name))
        # The name of the article 
        article_name = self._get_name(_from=x_wrapper_container)
        self._sa.logger.debug('Article name found : {}'.format(article_name))
        # The price label (it may be in format : from $xx)
        price_label = self._get_price(_from=x_wrapper_container)
        self._sa.logger.debug('Price found : {}'.format(price_label))
        # All the available colors
        available_colors = self._get_colors(_from=x_wrapper_container)
        self._sa.logger.debug('Colors found : {}'.format(available_colors))
        # All available sizes
        available_sizes = self._get_sizes(_from=article_container)
        self._sa.logger.debug('Sizes found : {}'.format(available_sizes))
        # The other details : Fit & Size, Material & Care, and Details
        other_details = self._get_extra_details(_from=article_container)
        self._sa.logger.debug('Extra details found : {}'.format(other_details))
        # Concatenate the details into one dictionary
        article_details = {'brand_name': brand_name,
                           'article_name': article_name,
                           'price_label': price_label,
                           'available_sizes': available_sizes,
                           'available_colors': available_colors,
                           'other_details': other_details}
        # Inform the end of processing the article.
        self._sa.logger.info("Finished successfully.")
        # Return the details
        return article_details
    
    def scrape(self, url: str = None):
        """
        Get all details of the article displayed in the current
        browser.
        
        """
        try: return self._scrape(url)
        # Catch the timeout exception that may raised
        # if the new tab took too much time to be loaded.
        except TimeoutException as e:
            # Log the trace to show the skipping cause.
            raise ArticleProcessingException("Skipped (Time out).",
                                             e, self._sa.logger).log()
        # Catch any other exceptions, and raise a
        # `ArticleProcessingException` exception.
        except BaseException as e:
            if isinstance(e, NoSuchWindowException):
                exc_message = ("NoSuchWindowException was "
                               "raised. Probably due to forcibly close "
                               "the Article's window.")
            elif isinstance(e, WebDriverException):
                exc_message = ("An unexpected Web Driver Exception "
                               "raised. Probably due to forcibly close "
                               "the browser.")
            else:
                exc_message = "Unexpected error."
            raise ArticleProcessingException(exc_message, e,
                                             self._sa.logger).dbg()
