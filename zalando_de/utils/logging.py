import logging
import inspect

# Handle import error on colorlog module.
try:
    import colorlog
    colorlog_imported = True
except ImportError:
    colorlog = None
    colorlog_imported = False

from zalando_de.utils.helpers import prefix_timer, rel_path


LEVELS_COLORS = {'DEBUG': 'cyan',
                 'INFO': 'green',
                 'WARNING': 'yellow',
                 'ERROR': 'red',
                 'CRITICAL': 'red,bg_white'}


def handle_level(level):
    """
    Handle Levels : Map the numeric levels to strings,
    and return it left-justified in a string of a width 9.

    """
    if isinstance(level, int):
        level = logging.getLevelName(level)
    # left-justify in a string of a width 9
    return level.ljust(9)

def get_called_from_filename():
    not_to_mention = ("logging.py", "helpers.py", "exceptions.py")
    go_back_by = 0
    while True:
        called_from = rel_path(inspect.stack()[go_back_by].filename)
        if called_from.endswith(not_to_mention):
            go_back_by += 1
            continue
        break
    return called_from


def init_handler(out: str = None):
    """
    Handle logging formatter.

    If `out` is not specified, return a Stream Handler
    with colorized formatter if the `colorlog` package is successfully
    imported, or with a simple formatter if not.

    Otherwise, return a File Handler, with a simple formatter.

    Parameters
    ----------

    `log` : str = None

        The path of the log file to stream the
        logging messages to.

    Returns
    -------

    logging.StreamHandler | logging.FileHandler
    
    """
    simple_format = '%(message)s'
    colorized_format = '%(log_color)s%(message)s%(reset)s'
    # If the  outpu log file id specified
    if out:
        # Define a simple formatter
        formatter = logging.Formatter(simple_format)
        # Define a File handler in append mode.
        handler = logging.FileHandler(out, encoding='utf-8', mode='a')
    # If not, an the colorlog is imported
    elif colorlog_imported:
        # Define a colorized formatter.
        formatter = colorlog.ColoredFormatter(colorized_format,
                                              log_colors=LEVELS_COLORS)
        # Define a Stream handler.
        handler = logging.StreamHandler()
    # Otherwise
    else:
        # Define a simple formatter
        formatter = logging.Formatter(simple_format)
        # Define a Stream handler.
        handler = logging.StreamHandler()
    # Finally, set the formatter to the handler.
    handler.setFormatter(formatter)
    # And return it
    return handler

class Logger():

    def __init__(self, out=None, min_level: int = 20) -> None:
        self.logger = logging.getLogger('scrapping_logger')
        self.config(out, min_level)

    def config(self, out, min_level):
        """
        Configure the logger.

        """
        # Set the level
        self.logger.setLevel(min_level)
        # If teh logger has already handlers, remove them
        if self.logger.handlers:
            for handler in self.logger.handlers:
                self.logger.removeHandler(handler)
        # And add a new handler.
        handler = init_handler(out)
        self.logger.addHandler(handler)

    def log(self, message, level=10, show_details=True, _lbr=False, _rbr=False):
        """
        Log a message with severity `level`.

        Parameters
        ----------

        `message` : str ( required )
            The message to log.

        `level` : str | int ( optional [ default = 10 ] )
            A parameter that indicates the level of the message to log.
            It must be either an integer (`0`, `10`, `20`, `30`, `40`, or
            `50`) or a string (`'NOTSET'`, `'DEBUG'`, `'INFO'`, `'WARNING'`,
            `'ERROR'` or `'CRITICAL'`)

        `show_details` : bool ( optional [ default = True ] )
            A boolean indicated whether to add datetime prefix or not.

        `_lbr` : bool ( optional [ default = False ] )
            A boolean indicates whether to log the message in a new line or not.
        
        """
        # Get the file name from which the log is called.
        called_from = get_called_from_filename()
        # Handle the level
        if isinstance(level, str):
            level = logging.getLevelName(level)
        # Add a suffix that includes the datetime, the level, the
        # filename if show_details is true.
        if show_details:
            message = ("{} [{}] {} : {}"
                       "".format(prefix_timer(),
                                 handle_level(level),
                                 called_from,
                                 message))
        # Add the new line to the left if _lbr set to True
        if _lbr:
            message = "\n{}".format(message)
        # Add the new line to the right if _rbr set to True
        if _rbr:
            message = "{}\n".format(message)
        # Log
        self.logger.log(level=level, msg=message)

    def debug(self, message, show_details=True, _lbr=False, _rbr=False):
        """
        Log a message with severity 'DEBUG'.

        For more details, see :meth:`Logger.log`
        
        """
        self.log(message, 10, show_details, _lbr, _rbr)

    def info(self, message, show_details=True, _lbr=False, _rbr=False):
        """
        Log a message with severity 'INFO'.

        For more details, see :meth:`Logger.log`
        
        """
        self.log(message, 20, show_details, _lbr, _rbr)

    def warn(self, message, show_details=True, _lbr=False, _rbr=False):
        """
        Log a message with severity 'WARNING'.

        For more details, see :meth:`Logger.log`
        
        """
        self.log(message, 30, show_details, _lbr, _rbr)

    def error(self, message, show_details=True, _lbr=False, _rbr=False):
        """
        Log a message with severity 'ERROR'.

        For more details, see :meth:`Logger.log`
        
        """
        self.log(message, 40, show_details, _lbr, _rbr)

    def critical(self, message, show_details=True, _lbr=False, _rbr=False):
        """
        Log a message with severity 'CRITICAL'.

        For more details, see :meth:`Logger.log`
        
        """
        self.log(message, 40, show_details, _lbr, _rbr)

    def debu0(self, *args, **kwargs): self.debug(*args, **kwargs)
    def inf0(self, *args, **kwargs): self.debug(*args, **kwargs)
    def erro0(self, *args, **kwargs): self.debug(*args, **kwargs)
