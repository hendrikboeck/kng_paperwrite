##
# @file
# @author Hendrik Boeck <hendrikboeck.dev@protonmail.com>
#
# @package   Paperwrite.PyAdditions.Io
# @namespace Paperwrite.PyAdditions.Io
#
# Package containing internal logger and io functions, this package will be
# initialized in the Paperwrite.Application.ApplicationContext.__init__
# function. Furthermore can this package be configured through the global
# configuration file in the section `io`
# (see Paperwrite.Configuration.IoConfiguration).
#
# @see
#   - Paperwrite.Application.ApplicationContext
#   - Paperwrite.Configuration.IoConfiguration

# -- STL
from datetime import datetime
import logging
import sys
import time

# -- LOCAL
from Paperwrite.Configuration import IoConfiguration

TZ_NAME = time.tzname[0]

##
# Name of logger, which will be used to write to CLI and to log file in package.
LOGGER_NAME = "ppw-logger"

##
# Logger object, which has LOGGER_NAME as identification. Will be independent
# from root logger of python, as it will not propage messages to it.
LOGGER = logging.getLogger(LOGGER_NAME)

##
# Dictionary, mapping configureable logger levels from configuration file to
# internal values from `logging` library.
LEVELS = {
    "DEBUG": logging.DEBUG,  # 10
    "INFO": logging.INFO,  # 20
    "WARNING": logging.WARN,  # 30
    "ERROR": logging.ERROR,  # 40
    "CRITICAL":
        logging.CRITICAL  # 50
}

##
# Dictionary mapping configureable CLI-streams from configuration file options
# to internal values from `sys` package.
IO_STREAMS = {"SYS:STDOUT": sys.stdout, "SYS:STDERR": sys.stderr}


##
# Class that creates a specific logging.Formatter for the CLI logger of LOGGER.
# Colors that are used for different logging levels can be configured via the
# static variable FORMATS. Colors use the prefix `\033`  (see
# https://misc.flogisoft.com/bash/tip_colors_and_formatting).
class ColoredCliFormatter(logging.Formatter):

  ##
  # @var FORMAT
  # Format string from `LOG_FORMATTER` with added general formating like bold
  # text and space reserved for levelname. Placeholder `%(logcolor)` is used for
  # later replacement with levelcolor.
  FORMAT = f"\033[1m%(asctime)s ({TZ_NAME}) %(logcolor)%(levelname)-8s\033[39m |\033[0m %(message)s"

  ##
  # @var DATETIME
  # Format string for formating the time inside log messages.
  DATETIME = "%Y/%m/%d %H:%M:%S"

  ##
  # @var FORMATS
  # Dictionary that holds specific value for placeholder `%(logcolor)` mapped to
  # different logging levels.
  FORMATS = {
      logging.DEBUG: FORMAT.replace("%(logcolor)", "\033[96m"),  # light cyan
      logging.INFO: FORMAT.replace("%(logcolor)", "\033[90m"),  # light gray
      logging.WARNING: FORMAT.replace("%(logcolor)",
                                      "\033[93m"),  # light yellow
      logging.ERROR: FORMAT.replace("%(logcolor)", "\033[91m"),  # light red
      logging.CRITICAL: FORMAT.replace("%(logcolor)",
                                       "\033[95m"),  # light magenta
  }

  ##
  # From `logging.Formatter.format`:
  #
  #  > Format the specified record as text. The record's attribute dictionary is
  #  > used as the operand to a string formatting operation which yields the
  #  > returned string. Before formatting the dictionary, a couple of
  #  > preparatory steps are carried out. The message attribute of the record is
  #  > computed using LogRecord.getMessage(). If the formatting string uses the
  #  > time (as determined by a call to usesTime(), formatTime() is called to
  #  > format the event time. If there is exception information, it is formatted
  #  > using formatException() and appended to the message.
  #
  # @param  record  specific log record
  # @return formated record as str
  def format(self, record: logging.LogRecord) -> str:
    logFmt = self.FORMATS.get(record.levelno)
    formatter = logging.Formatter(logFmt, self.DATETIME)
    return formatter.format(record)

  def GetPrefix(self, level: str) -> str:
    levelno = LEVELS.get(level)
    return self.FORMATS.get(levelno).replace(
        "%(asctime)s",
        datetime.now().strftime(self.DATETIME)).replace("%(levelname)-8s",
                                                        level.ljust(8)).replace(
                                                            "%(message)s", "")


##
# Global formatter object, which defines the formatting of logging messages
# printed to log file of logger.
LOG_FORMATTER = logging.Formatter(
    f"%(asctime)s ({TZ_NAME}) %(levelname)-8s | %(message)s",
    "%Y/%m/%d %H:%M:%S")

##
# Global formatter object, which defines the formatting of logging messages
# printed to cli output of logger.
CLI_FORMATTER = ColoredCliFormatter()


##
# Configures global variables and adds file- and cli-handler to logger. Is
# called from Paperwrite.Application.ApplicationContext.__init__ function.
#
# @param  conf  configuration from `io`-block from configuration file
#
# @see
#   - Paperwrite.Application.ApplicationContext
#   - Paperwrite.Configuration.IoConfiguration
def Configure(conf: IoConfiguration) -> None:
  global LOGGER, CLI_FORMATTER, LOG_FORMATTER, IO_STREAMS, LEVELS

  # get stream for console-handler
  consoleStream = IO_STREAMS.get(conf.LogStream, "SYS:STDERR")

  # create handlers for logger
  fileHandler = logging.FileHandler(conf.LogFilepath)
  consoleHandler = logging.StreamHandler(consoleStream)

  # get logging levels for handlers
  logLevelCli = LEVELS.get(conf.CliMode, LEVELS["INFO"])
  logLevelLog = LEVELS.get(conf.LogMode, LEVELS["WARNING"])
  # use lowest logging level specified above
  logLevelMin = min(logLevelCli, logLevelLog)

  # set logging level for logger and handlers
  LOGGER.setLevel(logLevelMin)
  fileHandler.setLevel(logLevelLog)
  consoleHandler.setLevel(logLevelCli)

  # set formatter for handlers
  fileHandler.setFormatter(LOG_FORMATTER)
  consoleHandler.setFormatter(CLI_FORMATTER)

  # add handlers to logger
  LOGGER.addHandler(fileHandler)
  LOGGER.addHandler(consoleHandler)

  # dont't propagate log messages to main logger
  LOGGER.propagate = False


##
# Alias for default python `print` function.
#
# This function is just an alias for the default `print` function of python. It
# is used so that all io operations are streamlined and can be altered in a
# single place.
#
# @example
# ~~~{.py}
# >>> from Paperwrite.PyAdditions import Io
# >>> Io.Print("Hello World!")
# Hello World
# ~~~
Print = print

##
# Alias for `logging.debug` function over static `LOGGER`.
#
# This function is just an alias for the `logging.debug` function over the
# static `LOGGER` variable. It is used so that all io operations are streamlined
# and can be altered in a single place.
#
# @example
# ~~~{.py}
# >>> from Paperwrite.PyAdditions import Io
# >>> Io.Debug("Hello World!")
# 2022/04/05 10:42:35 (UTC) DEBUG    | Hello World!
# ~~~
Debug = LOGGER.debug

##
# Alias for `logging.info` function over static `LOGGER`.
#
# This function is just an alias for the `logging.info` function over the
# static `LOGGER` variable. It is used so that all io operations are streamlined
# and can be altered in a single place.
#
# @example
# ~~~{.py}
# >>> from Paperwrite.PyAdditions import Io
# >>> Io.Info("Hello World!")
# 2022/04/05 10:42:08 (UTC) INFO     | Hello World!
# ~~~
Info = LOGGER.info

##
# Alias for `logging.warning` function over static `LOGGER`.
#
# This function is just an alias for the `logging.warning` function over the
# static `LOGGER` variable. It is used so that all io operations are streamlined
# and can be altered in a single place.
#
# @example
# ~~~{.py}
# >>> from Paperwrite.PyAdditions import Io
# >>> Io.Warning("Hello World!")
# 2022/04/05 10:41:28 (UTC) WARNING  | Hello World!
# ~~~
Warning = LOGGER.warning

##
# Alias for `logging.error` function over static `LOGGER`.
#
# This function is just an alias for the `logging.error` function over the
# static `LOGGER` variable. It is used so that all io operations are streamlined
# and can be altered in a single place.
#
# @example
# ~~~{.py}
# >>> from Paperwrite.PyAdditions import Io
# >>> Io.Warning("Hello World!")
# 2022/04/05 10:42:16 (UTC) ERROR    | Hello World!
# ~~~
Error = LOGGER.error

##
# Alias for `logging.critical` function over static `LOGGER`.
#
# This function is just an alias for the `logging.critical` function over the
# static `LOGGER` variable. It is used so that all io operations are streamlined
# and can be altered in a single place.
#
# @example
# ~~~{.py}
# >>> from Paperwrite.PyAdditions import Io
# >>> Io.Critical("Hello World!")
# 2022/04/05 10:41:34 (UTC) CRITICAL | Hello World!
# ~~~
Critical = LOGGER.critical
