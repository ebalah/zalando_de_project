from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException


from zalando_de.utils.helpers import timer
from zalando_de.scrape.commun.assistants import ScraperAssistant



class DeadScraperAssistantError(Exception):
    """
    An exception to handle browser closing errors,
    and validate the assistant.
    
    """


class ArticleScraper():

    """
    A context manager to manage articles in a new tab.
    
    """

    def __init__(self, assistant, article_element = None) -> None:
        # ...
        self._sa: ScraperAssistant = self._validate_assistant(assistant)
        self._article_element = article_element

    def __enter__(self):
        # Open a new tab to handle the article.
        self._sa._click_to_new_tab(self._article_element)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            raise
        # Close the opened tab and get back to the articles' page
        try:
            self._sa._close_and_get_back()
        except Exception:
            self._sa.logger.debug("Failed to get back the main tab.")
            raise

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
    
    def _get_link(self):
        """
        Get the link of an article page.
        
        """
        _link = self._sa.driver.current_url
        if not _link:
            self._sa.logger.warn("Unable to get the current url."
                                 "Maybe the page's still loading.")
            raise TimeoutException("Could not load the page.")
        return _link
            
    def _extract_ID(self, link: str):
        """
        Extract an id for an article from its link.

        """
        article_id = (link.replace('https://en.zalando.de/', '')
                          .replace('.html', ''))
        return article_id

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
        # search for 'pl0w2g DT5BTM A-NCMf' class and get alt attribute of img tag.
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

    def scrape(self):
        """
        Get all details of the article displayed in the current
        browser.
        
        """
        # Get the article link
        article_link = self._get_link()
        # Get the article's ID
        article_id = self._extract_ID(article_link)
        # Inform the start of processing the article.
        self._sa.logger.info("Processing article {} started."
                             "".format(article_link), _lbr=True)
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
        # Inform the end of processing the article.
        self._sa.logger.info("Processing finished successfully.")
        # Concatenate the details into one dictionary
        article_details = {'link': article_link,
                           'brand_name': brand_name,
                           'article_name': article_name,
                           'price_label': price_label,
                           'available_sizes': available_sizes,
                           'available_colors': available_colors,
                           'other_details': other_details,
                           'scraped_in': timer()}
        # Return the details
        return article_details, article_id