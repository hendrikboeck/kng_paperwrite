##
# @file
# @author Hendrik Boeck <hendrikboeck.dev@protonmail.com>
#
# @package   Paperwrite.Application
# @namespace Paperwrite.Application
#
# This package contains the application context object (AppContext). Furthermore
# actively initializes this package the Paperwrite.PyAdditions.Io package. It
# also parses the arguments from the command line.

# -- STL
from argparse import ArgumentParser, Namespace
from typing import NamedTuple

# -- PROJECT
from Paperwrite.Configuration import Configuration
from Paperwrite.PyAdditions import Io
from Paperwrite.PyAdditions.Types import Singleton


##
# This class will parse the cli for arguments predefined in `__init__` function
# of class. For help on arguments type `--help` flag onto CLI.
#
# ```{.bash}
# usage: pate-wapi [-h] [-c CONF]
#
# optional arguments:
#   -h, --help            show this help message and exit
#   -c CONF, --conf CONF  set custom filepath to configuration file
# ```
class CLIArgumentParser():

  ##
  # @var parser
  # internal ArgumentParser
  parser: ArgumentParser

  ##
  # Constructor
  def __init__(self) -> None:
    # initialize argument parser
    self.parser = ArgumentParser()

    # add cli-arguments to parser
    self.parser.add_argument("-c",
                             "--conf",
                             type=str,
                             default="ppw.yml",
                             required=False,
                             help="set custom filepath to configuration file")

  ##
  # Parse arguments from CLI.
  #
  # @return Parsed arguments from CLI as Namespace.
  def ParseArgs(self) -> Namespace:
    # return parsed arguments as Namespace
    return self.parser.parse_args()


class StorageLocations(NamedTuple):
  Temporary: str
  Mutable: str


STORAGE_LOCATIONS = dict(
    LOCAL=StorageLocations(Temporary="tmp", Mutable="store"),
    GLOBAL=StorageLocations(Temporary="/tmp/ppw-api-pdf-cache",
                            Mutable="store"),
)


##
# Context for application. Class/Instance, which holds all major information on
# running the program and connections to databases. It also configures the
# Paperwrite.PyAddiditions.Io package on `__init__()` function.
class ApplicationContext(Singleton):

  ##
  # @var Config
  # Configuration parsed from configuration file.
  Config: Configuration

  Store: StorageLocations

  ##
  # Constructor. Is called on `Init()` from inherited Singleton class.
  def __init__(self) -> None:
    # parse arguments from CLI
    argsParser = CLIArgumentParser()
    cliArgs = argsParser.ParseArgs()

    # map information to members
    self.Config = Configuration(cliArgs.conf)

    # configure io package
    Io.Configure(self.Config.Io)

    self.Store = STORAGE_LOCATIONS[self.Config.StorageOption]


##
# This is the application context object export for easier use and initializes
# it on program start.
AppContext = ApplicationContext.Instance()
