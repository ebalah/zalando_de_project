import argparse
import os

import pandas as pd
import json

from zalando_de.scrape.main import Scraper
from zalando_de.scrape.commun.assistants import ScraperAssistant
from zalando_de.utils.logging import Logger

def truncate_directory(output_dir):
    """
    Truncate the directory.

    """
    # get all the file names in the directory
    file_names = os.listdir(output_dir)
    # loop through each file name and remove it
    for file_name in file_names:
        file_path = os.path.join(output_dir, file_name)
        os.remove(file_path)

def parse_arguments():
    """
    Arguments parser.
    """
    parser = argparse.ArgumentParser(description='Zalando.de scrapping')
    # Add test argument.
    parser.add_argument('--test', action='store_true',
                        help='Executes the script in test mode')
    # Add restart argument.
    parser.add_argument('--trunc', action='store_true',
                        help='Removes all the previous outputs.')
    # Add output directory
    parser.add_argument('--odir', type=str, default=None,
                        help='Specifies the output directory.')
    # Specify logging level.
    parser.add_argument('--log_level', type=int, default=10,
                        help=('Specifies the minimum logging level (must '
                              'be used reduce the logging memory.)'))
    # Parse the arguments.
    args = parser.parse_args()
    # Retuen them.
    return args

def _create_directory_if_not_exists(path, trunc):
    """
    Create the directory if not exits.

    If trunc is not None, remove all the file in it.
    
    """
    try:
        os.makedirs(path)
    except FileExistsError:
        if trunc:
            truncate_directory(path)


def run():

    args = parse_arguments()

    # Handle the outputs destination directory
    if args.odir:
        output_dir = args.odir
    elif args.test :
        output_dir = f"{os.path.dirname(__file__)}/output_test"
    else :
        output_dir = f"{os.path.dirname(__file__)}/output"

    # Handle the data and logs folders.
    _create_directory_if_not_exists(f"{output_dir}/data", args.trunc)
    _create_directory_if_not_exists(f"{output_dir}/logs", args.trunc)
    
    data_output_dir = f"{output_dir}/data"
    log_output_file = f"{output_dir}/logs/logging.log"

    logger = Logger(log_output_file, args.log_level)

    # Initiate the Shared Helper Tool
    assistant = ScraperAssistant(logger=logger)

    # Initiate the scraper
    scraper = Scraper(assistant=assistant, out=data_output_dir)

    # Start scrapping
    scraper.scrape()
    
    # Save channels with no results it to a json file.
    scraper.save_to_json()

if __name__ == '__main__':
    run()
