import warnings
import time
import os

import package


# Path helpers

pkg_dir: str = os.path.dirname(package.__path__[0])

def get_relative_path(path: str):
    """
    Convert the absolute path to relative.
    
    """
    relative_path = os.path.relpath(path, start=pkg_dir)
    # Return relative_path with  replaced with /
    return relative_path.replace('\\', '/')


### Data helpers.

def datem():
    return time.strftime("[%b %d, %Y %H:%M:%S] ~ $")


def file_name_timer():
    return time.strftime("%Y%m%d_%H%M%S")


### Selenium helpers

def clean_text_number(text_number):
    """
    Clean a number provided in text.
    """
    # If text number is empty, return it
    if not text_number:
        return -1
    # Vectorize the text number.
    text_vector: list = text_number.lower().split()[:-1]
    # Concatenate the remaning elements and remove commas
    _text_number = ' '.join(text_vector).replace(',', '').strip()
    # Try to convert the text number to a numeric number.
    try:
        return int(_text_number)
    except:
        raise ValueError("The text_number {} could not be "
                         "cleaned.".format(text_number))
    
def clean_pagination_label(text_pagin):
    """
    Clean a pagination indexer provided in text.
    """
    # If text_pagin is empty, return -1
    if not text_pagin:
        return -1
    # Vectorize the text.
    text_vector: list = text_pagin.lower().split()
    # get the current page number, and the total of pages.
    _, current_page, _, totale_pages = text_vector
    # try to convert them to integers.
    try:
        current_page = int(current_page)
    except:
        raise RuntimeError("Couldn't cast {} to integer. "
                           "Provided text was : {}"
                           "".format(current_page, text_pagin))
    try:
        totale_pages = int(totale_pages)
    except:
        raise RuntimeError("Couldn't cast {} to integer. "
                           "Provided text was : {}"
                           "".format(totale_pages, text_pagin))
    return current_page, totale_pages
    

def PendingDeprecation(func):
    """
    A decorator to mark a function as deprecated.
    
    """
    # wrappe the function
    def wrapper_func(*args, **kwargs):
        func_name = func.__name__
        warnings.warn("Function {} is deprecated.", PendingDeprecationWarning)
        return func(*args, **kwargs)
    # return the wrapper
    return wrapper_func
    

__all__ = [
    'clean_text_number',
    'clean_pagination_label',
    'PendingDeprecation'
]