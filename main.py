import platform
import argparse
import traceback
import time
import os

import zalando_de
from zalando_de.scrape.main import Scraper
from zalando_de.scrape.commun.assistants import ScraperAssistant
from zalando_de.scrape.commun.exceptions import (BrowserAlreadyClosedException,
                                                 UnableToConnectException)
from zalando_de.utils.logging import Logger
from zalando_de.utils.helpers import create_directory


trunc_conformation_msg = ("\nYou specified to truncate the output "
                          "directory.\nDo you confirm ? (y/n) : ")

continuing_msg = ("\nThe browser was recently forcibly closed "
                  "or the internet connection was instable.\n"
                  "Do you want to re-try ? (y/n) : ")


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
    parser.add_argument('--log_level', type=int, default=20,
                        help=('Specifies the minimum logging level (must '
                              'be used reduce the logging memory.)'))
    # Parse the arguments.
    args = parser.parse_args()
    # Retuen them.
    return args


def run():

    print("Script started ...")
    print()
    print("Python       : {}".format(platform.python_version()))
    print("Zalando-de   : {}".format(zalando_de.__version__))

    args = parse_arguments()

    # Handle the outputs destination directory
    if args.odir:
        output_dir = args.odir
    elif args.test :
        output_dir = f"{os.path.dirname(os.path.abspath(__file__))}/output_test"
    else :
        output_dir = f"{os.path.dirname(os.path.abspath(__file__))}/output"

    truncate_output = False
    if args.trunc:
        if input(trunc_conformation_msg).lower().startswith('y'):
            truncate_output = True

    # Handle the data and logs folders.
    create_directory(f"{output_dir}/data", truncate_output)
    create_directory(f"{output_dir}/logs", truncate_output)
    
    data_output_dir = f"{output_dir}/data"
    
    log_output_file = f"{output_dir}/logs/logging.log"

    print()
    print("Output directory : {}".format(data_output_dir))
    print("Logs destination :  {}".format(log_output_file))

    # Define the logger
    logger = Logger(log_output_file, args.log_level)

    while True:

        # Start Processing (Scrapping)
        with ScraperAssistant(logger=logger) as assistant:

            try:
                scraper = Scraper(assistant=assistant, out=data_output_dir)
                scraper.scrape()
                logger.info("Processing finished successfully.",
                            _lbr=True, _rbr=True)
                break
                
            except KeyboardInterrupt:
                logger.error("Processing forcibly stopped using "
                            "keyboard : Ctrl + C",
                            _lbr=True, _rbr=True)
                logger.error(traceback.format_exc(), show_details=False)
                break
                
            except (BrowserAlreadyClosedException,
                    UnableToConnectException) as exc:
                logger.error("Processing Failed with an Error :",
                            _lbr=True, _rbr=True)
                exc.err()
                # Re-try
                time.sleep(2)
                if not input(continuing_msg).lower().startswith('y'):
                    break

            except BaseException as exc:
                logger.error("Unknown exception : ",
                            _lbr=True, _rbr=True)
                logger.error(traceback.format_exc(), show_details=False)
                break

if __name__ == '__main__':
    run()
