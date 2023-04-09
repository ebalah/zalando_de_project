import time
import os

import zalando_de


# Path helpers

pkg_dir: str = os.path.dirname(zalando_de.__path__[0])

def rel_path(path: str):
    """
    Convert the absolute path to relative.
    
    """
    relative_path = os.path.relpath(path, start=pkg_dir)
    # Return relative_path with  replaced with /
    return relative_path.replace('\\', '/')


### Date helpers.

def prefix_timer():
    return time.strftime("[%b %d, %Y %H:%M:%S] ~ $")


def suffix_timer():
    return time.strftime("%Y%m%d_%H%M%S")

def current_datetime():
    return time.strftime("%A, %B %d, %Y %I:%M:%S %p")


### Selenium helpers

def total_items(text: str):
    """
    Clean a number provided in text.
    """
    # If text number is empty, return it
    if not text:
        return -1
    # Vectorize the text number.
    text_vector: list = text.lower().split()[:-1]
    # Concatenate the remaning elements and remove commas
    _total_items = ' '.join(text_vector).replace(',', '').strip()
    # Try to convert the text number to a numeric number.
    try:
        return int(_total_items)
    except:
        raise ValueError("The text {} could not be "
                         "cleaned.".format(text))
    
def total_pages(text: str):
    """
    Clean a pagination indexer provided in text.
    """
    # If text is empty, return -1
    if not text:
        return -1
    # Vectorize the text.
    text_vector: list = text.lower().split()
    # get the current page number, and the total of pages.
    _, current_page, _, totale_pages = text_vector
    # try to convert them to integers.
    try:
        current_page = int(current_page)
    except:
        raise RuntimeError("Couldn't cast {} to integer. "
                           "Provided text was : {}"
                           "".format(current_page, text))
    try:
        totale_pages = int(totale_pages)
    except:
        raise RuntimeError("Couldn't cast {} to integer. "
                           "Provided text was : {}"
                           "".format(totale_pages, text))
    return current_page, totale_pages
    
    

__all__ = [
    'rel_path',
    'prefix_timer',
    'suffix_timer',
    'current_datetime',
    'total_items',
    'total_pages'
]