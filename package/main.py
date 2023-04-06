import argparse
import os

import pandas as pd
import json

from package.utils.logging import Logger
from package.utils.helpers import file_name_timer
from package.scrape.main import Scrapper
from package.scrape.commun.assistants import ScrappingAssistant


def truncate_output_directory(output_dir, logger: Logger):
    """
    Truncate the output directory.

    """
    # get all the file names in the directory
    file_names: list[str] = os.listdir(output_dir)
    logger.log("Truncating the {} directory ...".format(output_dir))
    # loop through each file name and remove it
    for file_name in file_names:
        if not file_name.endswith('.log'):
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
    # Parse the arguments.
    args = parser.parse_args()
    # Retuen them.
    return args


def run():
    """
    Execute the the script for testing some channels:

        python ./_09/package/main.py --test

    Execute the script :

        python ./_09/package/main.py

    """

    args = parse_arguments()

    # Check if the script is to be run on test mode.
    is_test = True if args.test else False

    # The current directory (must be package/)
    curr_dir = os.path.dirname(__file__)
    # The directory where the outputs are expected to be saved.
    output_dir = f"{curr_dir}\\output"

    log_output = f"{output_dir}\\log_output_{file_name_timer()}.log"

    logger = Logger(log_output)

    # Clear the output directory
    truncate_output_directory(output_dir, logger)

    ### NOTE: ONLY FOR TESTING ############################################
    if is_test:
        ...
    #######################################################################

    # Initiate the Shared Helper Tool
    assistant = ScrappingAssistant(logger=logger)

    # Initiate the scrapper
    scrapper = Scrapper(logger=logger)

    # Start scrapping
    scrapper.scrape()
    
    # Save channels with no results it to a json file.
    products_json = scrapper.to_dict()

    # Convert the cleaned data into a pandas dataframe.
    products_dataframe = scrapper.to_pandas()

    # Save the dataframe into excel file.
    csv_output_file = f"{output_dir}\\data_output.xlsx"

    # Save the final results to the file.
    # products_dataframe.to_csv(csv_output_file, index=False)


if __name__ == '__main__':
    run()
