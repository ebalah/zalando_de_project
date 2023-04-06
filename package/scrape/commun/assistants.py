import time

import numpy as np

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


from package.utils.logging import Logger
from package.utils.helpers import *

PROFILE = webdriver
WEB_DRIVER = webdriver.Edge
OPTIONS = webdriver.EdgeOptions
WEB_ELEMENT = WebElement

XLONG_WAIT = 20
LONG_WAIT = 10
MEDIUM_WAIT = 7
SHORT_WAIT = 5


class ScrappingAssistant():

    def __init__(self, driver = None, logger = None) -> None:
        # Configure the helper tool
        self.__config(driver, logger)
    
    def __config_driver(self, driver):
        self.driver: webdriver.Edge = driver or self._init_driver()

    def __config_logger(self, logger):
        self.logger: Logger = logger or Logger()

    def __config_wait(self):
        self.xlong_wait = WebDriverWait(self.driver, XLONG_WAIT)
        self.long_wait = WebDriverWait(self.driver, LONG_WAIT)
        self.medium_wait = WebDriverWait(self.driver, MEDIUM_WAIT)
        self.short_wait = WebDriverWait(self.driver, SHORT_WAIT)

    def __config(self, driver, logger, *args, **kwargs):
        self.__config_logger(logger)
        self.__config_driver(driver)
        self.__config_wait( *args, **kwargs)

    def _init_driver(self):
        """
        Initiate the driver.
        
        """
        # create a new instance of the Edge options
        options = OPTIONS()
        # set the driver window's to start maximized.
        options.add_argument("start-maximized")
        # create a new instance of the Edge driver with the options
        return WEB_DRIVER(options=options)

    def _sleep_t_sec(self, t: float = 1, _coef = .3):
        """
        Sleep for x seconds.
        
        """
        t = _coef * np.random.ranf() + t
        time.sleep(t)

    def _wait_to_load(self, t: float = 2, _coef = .7):
        """
        Sleep for ~2 seconds to wait the page to be fully
        loaded.

        """
        t = _coef * np.random.ranf() + t
        self._sleep_t_sec(t)

    def _scroll_to(self, scroll_to: float | WEB_ELEMENT):
        """
        Scroll up/down to `scroll_to`
        
        """
        # If scroll to is a web element, then get the y location of
        # the element to scroll to.
        if not isinstance(scroll_to, (float, int)):
            scroll_to = scroll_to.location['y']
        # Otherwise, scroll_to must be a floating number.
        self.driver.execute_script("window.scrollTo(0, {})"
                                   "".format(scroll_to))

    def _sleep_and_scroll(self, scroll_to: float, _coef: float = .3):
        """
        Sleep and scroll to mimic the human behavior.

        """
        # randomize the time to sleep.
        t = _coef * np.random.ranf()
        # Sleep for t seconds
        self._sleep_t_sec(t)
        # Scroll down to scroll_to_1 point.
        self._scroll_to(scroll_to)
        
        
    def sleep_and_scroll(self, scroll_to: float | WEB_ELEMENT = 'randomly'):
        """
        Sleep and scroll to mimic the human behavior.

        """
        # The default times to scroll
        _n = 1
        # The interval of time to sleep for each scroll : (0, _coef]
        # an the maximum of time to scroll in.
        # NOTE: To minimize the time of scrolling, _n * _coef must
        # be less than 4 seconds.
        _coef = .3
        _max_time = 4
        # The random value to substract from scrool_to. This must
        # help to avoit placing the pointer to the top of the screen. 
        _rand = 80
        # The random pixels to substract from scroll_to.
        _s_rand = np.random.randint(40, _rand)
        # The maximum value to scroll each time
        _max_unit = 800
        # Get the current y position.
        current_y_location = self.driver.execute_script('return window.scrollY;')
        # If scroll_to == 'randomly', use the current location asthe
        # next value to scroll to. (adding _s_rand ensure the scrolling)
        if isinstance(scroll_to, str):
            scroll_to = current_y_location + _s_rand
        # If scroll to is a web element, then get the y location of
        # the element to scroll to.
        if not isinstance(scroll_to, (float, int)):
            scroll_to = scroll_to.location['y']
        # Substract _s_rand from scroll_to.
        scroll_to = (scroll_to - _s_rand
                     if scroll_to - _s_rand > 0
                     else scroll_to * 0.6)
        # Calculate the difference between current location and
        # the location to scroll to.
        scroll_by: float = abs(current_y_location - scroll_to)
        # Overwrite _n if this difference is too large.
        _n = max(_n, int(scroll_by // _max_unit))
        # Ensure that _n * _coef is less than 4 seconds.
        if _n * _coef > _max_time:
            _coef = _max_time / _n
        # define the scroll units : the positions to scroll to
        # each time untill we reach scroll_to in the nth time.
        scroll_to_unit = (np.linspace(current_y_location, scroll_to, _n + 1)
                          if scroll_to != 'randomly'
                          else ['randomly', 'randomly'])
        # Sleep and scroll for n times.
        for _scroll_to in scroll_to_unit[1:]:
            self._sleep_and_scroll(_scroll_to, _coef=_coef)

    def _move_mouse_to(self, element: WEB_ELEMENT):
        """
        Move the mouse to focus on `element` and scroll to it.

        """
        # Scroll to the element.
        self.sleep_and_scroll(element)
        # Move the cursur to focus the element.
        ActionChains(self.driver).move_to_element(element).perform()
        # Sleep for half second.
        self._sleep_t_sec(.5)
        # Return the element
        return element

    def _move_mouse_to_and_click(self, element):
        """
        Move the mouse to focus on `element`, scroll to it,
        and then click it.

        """
        # Scroll to the element and move the cursur to focus
        # on it. Finally click the element.
        self._move_mouse_to(element).click()

    def _click_to_new_tab(self, element: WEB_ELEMENT):
        """
        Click an element to open a new tab.

        """
        # Scroll to the element and move the cursur to focus on it.
        self._move_mouse_to(element)
        # Open a new tab by clicking element.
        (ActionChains(self.driver).key_down(Keys.CONTROL)
                                  .click(element)
                                  .key_up(Keys.CONTROL)
                                  .perform())
        # switch to the new tab
        self.driver.switch_to.window(self.driver.window_handles[-1])
        # Wait the new tab to load.
        self._wait_to_load()

    def _close_and_get_back(self):
        """
        Close the current tab, and get back to the previous one.

        """
        # Close the current tab.
        self.driver.close()
        # switch to the last tab
        self.driver.switch_to.window(self.driver.window_handles[-1])
        # Mimic the human behavior
        self._sleep_t_sec()

    def _get_class_css_selector(self, class_names: str = None):
        """
        Given a set of class names, return a css selector.
        
        """
        # Genrate the css selector by class_names
        return "." + class_names.replace(' ', '.')

    def _get_id_css_selector(self, class_names: str = None):
        """
        Given a id, return a css selector.
        
        """
        # Genrate the css selector by id_name
        return "#" + class_names

    def _get_class_locator(self, class_names: str):
        """
        Given a set of class names, return a locator
        by css selector.
        
        """
        # Genrate the css selector by class names
        css_selector = self._get_class_css_selector(class_names)
        # Return the locator.
        return (By.CSS_SELECTOR, css_selector)
    
    def _get_id_locator(self, id_name: str = None):
        """
        Given an id name, return a locator by css
        selector.
        
        """
        # Genrate the css selector by id name
        css_selector = self._get_id_css_selector(id_name)
        # Return the locator.
        return (By.CSS_SELECTOR, css_selector)

    def _get_name_locator(self, name: str):
        """
        Get locator by Name attribute.
        
        """
        return (By.NAME, f"//*[@name='{name}']")

    def _get_tag_locator(self, name: str):
        """
        Get locator by tage name.
        
        """
        return (By.TAG_NAME, name)

    
    def _get_locator(self, value: str, by: str = 'class'):
        """
        Get locator by Class names, id, name attribute, or
        tag name.
        
        """
        # Get locator
        if by == 'class':
            return self._get_class_locator(value)
        if by == 'id':
            return self._get_id_locator(value)
        if by == 'name':
            return self._get_name_locator(value)
        if by == 'tag':
            return self._get_tag_locator(value)
        # Otherwise raise ValueError exception.
        raise ValueError("Invalid 'by' argument.")

    def _get_element(self, element_locator: tuple,
                     parent_element: WEB_ELEMENT = None):
        """
        Seek for a web element in `parent_element` using the
        `element_locator` locator.

        """
        # If the container web element is provided, search for the
        # targeted element in this container
        if parent_element:
            return parent_element.find_element(*element_locator)
        # Otherwise, search in the global one (self.driver)
        self.short_wait.until(ec.presence_of_element_located(element_locator))
        # Get the element and return it
        return self.driver.find_element(*element_locator)
    
    def _get_element_by_class(self, class_names: str,
                             parent_element: WEB_ELEMENT = None):
        """
        Get the web element, by searching it by
        class names.

        """
        # Get the locator
        element_locator = self._get_class_locator(class_names)
        # Get the element.
        element = self._get_element(element_locator, parent_element)
        # Return the element
        return element
    
    def _get_element_by_id(self, id_name: str,
                           parent_element: WEB_ELEMENT = None):
        """
        Get the web element, by searching it by id.

        """
        # Get the locator
        element_locator = self._get_id_locator(id_name)
        # Get the element.
        element = self._get_element(element_locator, parent_element)
        # Return the element
        return element
    
    def _get_element_by_name(self, name: str,
                             parent_element: WEB_ELEMENT = None):
        """
        Get the web element, by searching it by
        name attribute.

        """
        # Get locator
        element_locator = self._get_name_locator(name)
        # Get the element.
        element = self._get_element(element_locator, parent_element)
        # Return the element
        return element
    
    def _get_element_value(self, element_locator: tuple,
                           parent_element: WEB_DRIVER = None):
        """
        Search for an element in `parent_element`, and return it's
        value (visible text content).

        """
        # Get the element
        element = self._get_element(element_locator, parent_element)
        # Return the value
        return element.get_attribute('innerText')
    
    def _get_element_value_by_class(self, class_names: str,
                                    parent_element: WEB_ELEMENT = None):
        """
        Search for an element by its class names in `parent_element`,
        and return it's value.

        """
        # Get the locator
        element_locator = self._get_class_locator(class_names)
        # Get the value
        return self._get_element_value(element_locator,
                                       parent_element)
    
    def _get_element_value_by_id(self, id_name: str,
                                 parent_element: WEB_ELEMENT = None):
        """
        Get the element value , by searching the element by id.

        """
        # Get the locator
        element_locator = self._get_id_locator(id_name)
        # Get the value
        return self._get_element_value(element_locator, parent_element)
    
    def _get_element_value_by_name(self, name: str,
                                   parent_element: WEB_ELEMENT = None):
        """
        Get the element value , by searching the element by
        name attribute.

        """
        # Get the locator
        element_locator = self._get_name_locator(name)
        # Get the value
        return self._get_element_value(element_locator, parent_element)
    
    def _get_elements(self, elements_locator: tuple,
                      parent_element: WEB_DRIVER = None):
        """
        Given a locator, get the all the elements present in
        `parent_element` web element if provided, or in the global element
        (`self.driver`) otherwise.

        """
        # If the container web element is provided, search for the
        # targeted element in this container
        if parent_element: return parent_element.find_elements(*elements_locator)
        # Otherwise, search in the global one (self.driver)
        self.short_wait.until(ec.presence_of_element_located(elements_locator))
        # Get the list of elements and return them.
        return self.driver.find_elements(*elements_locator)
    
    def _get_elements_by_class(self, class_names: str,
                               parent_element: WEB_DRIVER = None):
        """
        Given a class names, get the all the elements present in
        `parent_element` web element if provided, or in the global element
        (`self.driver`) otherwise.

        """
        # Get the locator
        elements_locator = self._get_class_locator(class_names)
        # Get the elements
        elements = self._get_elements(elements_locator, parent_element)
        # Return the element
        return elements
    
    def _get_elements_by_id(self, id_name: str,
                            parent_element: WEB_DRIVER = None):
        """
        Given an id, get the all the elements present in
        `parent_element` web element if provided, or in the global element
        (`self.driver`) otherwise.

        """
        # Get the locator
        elements_locator = self._get_id_locator(id_name)
        # Get the elements
        elements = self._get_elements(elements_locator, parent_element)
        # Return the element
        return elements
    
    def _get_elements_by_name(self, name: str,
                               parent_element: WEB_DRIVER = None):
        """
        Given a class names, get the all the elements present in
        `parent_element` web element if provided, or in the global element
        (`self.driver`) otherwise.

        """
        # Get the locator
        elements_locator = self._get_name_locator(name)
        # Get the elements
        elements = self._get_elements(elements_locator, parent_element)
        # Return the element
        return elements