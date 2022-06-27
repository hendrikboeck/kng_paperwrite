##
# @file
# @author Hendrik Boeck <hendrikboeck.dev@protonmail.com>
#
# @package   Paperwrite.PyAdditions.Errors
# @namespace Paperwrite.PyAdditions.Errors
#
# Package containing additional Error types.


##
# Alias for builtin Exception class.
class Error(Exception):
  pass


##
# Error for a not supported feature, function, etc..
class NotSupportedError(Error):
  pass
