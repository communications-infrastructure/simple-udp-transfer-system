import logging
import logging.handlers as hl
import sys
from datetime import datetime
import sys
import os
import traceback


class ColorFormatter(logging.Formatter):

    # ANSI codes are a bit weird to decipher if you're unfamiliar with them, so here's a refresher
    # It starts off with a format like \x1b[XXXm where XXX is a semicolon separated list of commands
    # The important ones here relate to colour.
    # 30-37 are black, red, green, yellow, blue, magenta, cyan and white in that order
    # 40-47 are the same except for the background
    # 90-97 are the same but "bright" foreground
    # 100-107 are the same as the bright ones but for the background.
    # 1 means bold, 2 means dim, 0 means reset, and 4 means underline.

    LEVEL_COLOURS = [
        (logging.DEBUG, '\x1b[40;1m'),
        (logging.INFO, '\x1b[34;1m'),
        (logging.WARNING, '\x1b[33;1m'),
        (logging.ERROR, '\x1b[31m'),
        (logging.CRITICAL, '\x1b[41m'),
    ]

    FORMATS = {
        level: logging.Formatter(
            f'\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[35m%(name)s\x1b[0m %(message)s',
            f'%Y-%m-%d %H:%M:%S',
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f'\x1b[31m{text}\x1b[0m'

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output


def define_log():
    # Logging config, logging outside the github repo
    try:
        if os.name != 'nt':
            os.makedirs('/home/client/logs')
        else:
            os.makedirs('./client/logs')
    except FileExistsError:
        pass
    if os.name != 'nt':
        log_filename = '/home/client/logs/' + \
            datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '-log.txt'
    else:
        log_filename = "./client/logs/" + \
            datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '-log.txt'

    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColorFormatter()
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s %(message)s', f"%Y-%m-%d %H:%M:%S")

    # Print debug
    level = logging.DEBUG
    # Print to file, change file everyday at 12:00 Local
    date = datetime(2020, 1, 1, 12)
    file_handler = hl.TimedRotatingFileHandler(
        log_filename, when='midnight', atTime=date)
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)

    return console_handler, file_handler


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


def exception_to_log(log, traceback_message):
    log.error("An exception has ocurred while running the client:")
    exc = traceback.format_exception(traceback_message)
    for line in exc:
        line = line.rstrip().splitlines()
        for splits in line:
            log.error(splits)
