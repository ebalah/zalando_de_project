import time
import os

import zalando_de


# Privat helpers

def _euc_div(dividend, divisor):
    """
    Perform an euclidean division, and return
    the quotient and the remainder.
    
    """
    remainder = dividend % divisor
    quotient = int(dividend / divisor)
    return quotient, remainder


def _truncate_directory(output_dir):
    """
    Truncate the directory.

    """
    # get all the file names in the directory
    file_names = os.listdir(output_dir)
    # loop through each file name and remove it
    for file_name in file_names:
        file_path = os.path.join(output_dir, file_name)
        os.remove(file_path)

def create_directory(path, trunc):
    """
    Create the directory if not exits.

    If trunc is not None, remove all the file in it.
    
    """
    try:
        os.makedirs(path)
    except FileExistsError:
        if trunc:
            _truncate_directory(path)
    return path

# Path helpers

pkg_dir: str = os.path.dirname(zalando_de.__path__[0])

def rel_path(path: str):
    """
    Convert the absolute path to relative.
    
    """
    relative_path = os.path.relpath(path, start=pkg_dir)
    # Return relative_path with  replaced with /
    return relative_path.replace('\\', '/')

def norm_path(path: str):
    """
    Normalize a path.
    """
    return os.path.normpath(path)

def is_a_directory(dir_path):
    """
    Verify if a directory exists.

    """
    dir_path = os.path.normpath(dir_path)
    return os.path.exists(dir_path)


### Date helpers.

def timer():
    return time.strftime("%b %d, %Y %H:%M:%S")

def prefix_timer():
    return time.strftime("[%b %d, %Y %H:%M:%S] ~ $")


def suffix_timer():
    return time.strftime("%Y%m%d_%H%M%S")

def current_datetime():
    timestamp = time.time()
    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S",
                                  time.localtime(timestamp))
    return timestamp, timestamp_str

def delta_datetime(t_1: float, t_2: float):
    """
    Extract days, hours, minutes, and seconds
    from a delta of two moments given in seconds.

    """
    # t_2 is expected to be greater than t_1. So if it's
    # not, swap the given times.
    if t_1 > t_2:
        t_2, t_1 = t_1, t_2
    # Get days
    days, delta_t = _euc_div(t_2 - t_1, 86400)
    # Get hours
    hours, delta_t = _euc_div(delta_t, 3600)
    # Get minutes and seconds
    minutes, seconds = _euc_div(delta_t, 60)
    # Return a string of the combined extracted date units.
    return ("{} days, {} hours, {} minutes, and {:.3f} "
            "seconds".format(days, hours, minutes, seconds))


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
    'norm_path',
    'is_a_directory',
    'create_directory',
    'timer',
    'prefix_timer',
    'suffix_timer',
    'current_datetime',
    'delta_datetime',
    'total_items',
    'total_pages'
]