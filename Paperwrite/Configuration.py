##
# @file
# @author Hendrik Boeck <hendrikboeck.dev@protonmail.com>
#
# @package   Paperwrite.Configuration
# @namespace Paperwrite.Configuration
#
# This package contains the virtual structure of the configuration file for the
# application. Every block in the configuration file has its own wrapper as a
# NamedTuple. Some fields/values are already proccessed further (like the keys
# for the webserver configuration, which are already loaded as binary). In the
# below a example configuration file can be sound with default values for their
# respective key.
#
# The default configuration file is saved loaded from
# `/pate-wapi.yml`, if you want to use a custom location, you have to use the
# `-c` or `--conf` flag (see Paperwrite.Application.CLIArgumentParser).
#
# @example
# ~~~{.py}
# # pate-wapi.yml -- defaults
#
# database:
#   database: "database"
#   user: "user"
#   password: "password"
#   host: "127.0.0.1"
#   port: 5432
#
# webserver:
#   host: "127.0.0.1"
#   port: 44997
#   api-prefix: ""
#
# jwt-rs256:
#   private_key: "/jwt_rs256"
#   public_key: "/jwt_rs256.pub"
#
# io:
#   cli_mode: "info"
#   log_mode: "warning"
#   log_filepath: "pate-wapi-<ISO datetime>.log"
#   #log_directory: "/tmp"
#   log_stream: "sys:stderr"
# ~~~
#
# @see
#  - WebserverConfiguration
#  - DatabaseConfiguration
#  - JwtRS256Configuration
#  - IoConfiguration

# -- STL
import os
import sys
from datetime import datetime
from typing import NamedTuple

# -- LIBRARY
import yaml


##
# Representation of configureable parameters of Webserver (flask or
# waitress) and API from configuration file.
#
# @param  Host  `str` -- Dns or ip of current host on which the server should be
# listening (`0.0.0.0` to listen to all incoming traffic)
# @param  Port  `int` -- Port of current host on which the server should be
# listening
# @param  ApiPrefix  `str` -- Prefix of api that is added in front of all path's
#
# @par Configuration (defaults)
# ~~~{.py}
# webserver:
#   host: "127.0.0.1"
#   port: 44997
#   api-prefix: ""
# ~~~
#
# @see
#  - Paperwrite.Configuration
class WebserverConfiguration(NamedTuple):
  Host: str
  Port: int
  ApiPrefix: str


##
# Representation of configurable io/logging of program.
#
# @param CliMode  `str` -- Level for CLI logging mode as string
# @param LogMode  `str` --Level for logging to file as string
# @param LogFilepath  `str` -- Filepath to logfile as string
# @param LogStream  `str` -- Stream which should be logged to as string
#
# @par Configuration (defaults)
# ~~~{.py}
# io:
#   cli_mode: "info"
#   log_mode: "warning"
#   log_filepath: "pate-wapi-<ISO datetime>.log"
#   #log_directory: "/tmp"
#   log_stream: "sys:stderr"
# ~~~
#
# @see
#  - Paperwrite.Configuration
class IoConfiguration(NamedTuple):
  CliMode: str
  LogMode: str
  LogFilepath: str
  LogStream: str


##
# Representation of the sum of all configureable parameters and
# namespaces found in configuration file.
#
# @see
#  - Paperwrite.Configuration
#  - WebserverConfiguration
#  - DatabaseConfiguration
#  - JwtRS256Configuration
#  - IoConfiguration
class Configuration():

  ##
  # @var Webserver
  # Namespace for webserver configuration
  # @see
  #  - WebserverConfiguration
  Webserver: WebserverConfiguration

  ##
  # @var Io
  # Namespace for io configuration
  # @see
  #   - IoConfiguration
  Io: IoConfiguration

  StorageOption: str

  ##
  # Constructor
  #
  # @param  filepath  path to configuration file (default: `/pate-wapi.yml`)
  def __init__(self, filepath: str) -> None:
    try:
      # load configuration file from specified filepath
      with open(filepath, "r") as fstream:
        # parse yaml to Dict[str, Any]
        confd = yaml.safe_load(fstream)
    except FileNotFoundError as err:
      # abort program if no configuration file was found
      print(f"file could not be found: {err}", file=sys.stderr)
      exit(1)

    # map webserver namespace onto member
    webserverd = confd.get("webserver", {})
    self.Webserver = WebserverConfiguration(webserverd.get("host", "127.0.0.1"),
                                            int(webserverd.get("port", 44777)),
                                            webserverd.get("api_prefix", ""))

    # get io configuration block from file
    iod = confd.get("io", {})
    # get path for log to save to
    logFilepath = iod.get("log_filepath")
    # if no filepath is given set default path
    if logFilepath is None:
      # get current datetime in ISO format
      currentdt = datetime.now().isoformat()
      # set filepath to local default
      logFilepath = f"ppw-api-{currentdt}.log"
      # check if logs should be saved in a specific directory
      logDirectory = iod.get("log_directory")
      # change directory, if one is provided
      if logDirectory is not None:
        # create directory, if it does not exist
        os.makedirs(logDirectory, exist_ok=True)
        # append directory path to front of local filepath
        logFilepath = os.path.join(logDirectory, logFilepath)
    # map all values to IoConfiguration format
    self.Io = IoConfiguration(
        iod.get("cli_mode", "info").upper(),
        iod.get("log_mode", "warning").upper(),
        logFilepath,
        iod.get("log_stream", "sys:stderr").upper(),
    )

    self.StorageOption = confd.get("storage_option", "local").upper()
