##
# @file
# @author Hendrik Boeck <hendrikboeck.dev@protonmail.com>
#
# @package   Paperwrite
# @namespace Paperwrite
#
# Main package containing Main function of program, as well as all subpackages
# used in Paperwrite.
#
# @mainpage Paperwrite Knowledge Graph API

##
# Version of package/program
__version__ = "0.0.1"

# -- PACKAGE, SELF
from . import PyAdditions
from . import Application
from . import Configuration
from . import Rest
from . import RocketRouter
