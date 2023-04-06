import logging
import colorlog
import inspect

from package.utils.helpers import datem, get_relative_path


LEVELS_INT = {10: 'DEBUG',
              20: 'INFO',
              30: 'WARNING',
              40: 'ERROR',
              50: 'CRITICAL'}

LEVELS_STR = {v: k for k, v in LEVELS_INT.items()}


def adjust_level(level):
    if not isinstance(level, str):
        level = LEVELS_INT.get(level, '')
    return level.ljust(9)


class Logger():

    levels = {'DEBUG': 10,
              'INFO': 20,
              'WARNING': 30,
              'ERROR': 40,
              'CRITICAL': 50}

    def __init__(self, out=None) -> None:
        self._logger = logging.getLogger('scrapping_logger')
        self._customize(out)

    def _customize(self, out):
        # Set the level
        self._logger.setLevel(logging.DEBUG)
        # If an output file is provided, configure to output
        # the logs to a file
        if not self._logger.handlers and out:
            handler = logging.FileHandler(out, encoding='utf-8', mode='w')
            logging.Formatter(fmt='%(message)s')
            self._logger.addHandler(handler)
        # Othewise, configure to stream the output to terminal
        elif not self._logger.handlers:
            formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(message)s%(reset)s',
                log_colors={'DEBUG': 'cyan',
                            'INFO': 'green',
                            'WARNING': 'yellow',
                            'ERROR': 'red',
                            'CRITICAL': 'red,bg_white'})
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def log(self, message, level=10, exclude_datetime=False, _br=False):
        # Get the file name from which the log is called.
        called_from = get_relative_path(inspect.stack()[1].filename)
        if isinstance(level, str):
            level = LEVELS_STR.get(level, 0)
        if not exclude_datetime:
            message = f"{datem()} [{adjust_level(level)}] {called_from} : {message}"
        if _br:
            message = "\n" + message
        self._logger.log(level=level, msg=message)
