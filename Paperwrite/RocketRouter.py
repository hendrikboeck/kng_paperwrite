##
# @file
# @author Hendrik Boeck <hendrikboeck.dev@protonmail.com>
#
# @package   Paperwrite.RocketRouter
# @namespace Paperwrite.RocketRouter
#
# Package containing REST routing capabilities of RocketRouter.

# -- FUTURE (subject to change, handle with care)
#from __future__ import annotations

# -- STL
import os
import re
from datetime import datetime
from enum import Enum
from types import FunctionType
from typing import Any, Dict, List, NamedTuple, Optional, Pattern, Tuple

# -- LIBRARY
from flask import Response, request, Flask
from flask_cors import CORS

# -- LOCAL
from Paperwrite.Application import AppContext
from Paperwrite.PyAdditions import Io
from Paperwrite.PyAdditions.Errors import NotSupportedError, Error
from Paperwrite.Rest import CreateResponseJson, HttpStatus, RespondWithError


##
# Representation tuple for values in RocketPathVariableTypes enum.
#
# @param  t `type` -- Python type of RocketPathVariableType
# @param  regex   `str` -- Regular expression for RocketPathVariableType
class RocketPathVariableTypesRepresentation(NamedTuple):
  t: type
  regex: str


##
# Enum of type identifiers for variables in api-paths. Enum objects hold
# python internal type and regex-expression for variable-type.
#
#  - `uuid4` -- UUID version 4
#  - `str` -- strings without "/"
#  - `int64` -- integers 64bit
#  - `float64` -- floats 64bit
#
class RocketPathVariableTypes(Enum):

  ##
  # `uuid4` -- UUID version 4
  UUID4 = RocketPathVariableTypesRepresentation(
      str,
      "[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}")

  ##
  # `str` -- strings without "/"
  STR = RocketPathVariableTypesRepresentation(str, "[-a-zA-Z0-9@:%._\+~#=]+")

  ##
  # `int64` -- integers 64bit
  INT64 = RocketPathVariableTypesRepresentation(int, "[-+]?\d+")

  ##
  # `float64` -- floats 64bit
  FLOAT64 = RocketPathVariableTypesRepresentation(float, "[-+]?\d*\.?\d+|\d+")

  @staticmethod
  ##
  # Converts enum-object in string descriptor in lowercase.
  #
  # @param  t type as enum-object
  #
  # @return enum-object as lowercase string descriptor
  def ToStr(t) -> str:
    return t._name_.lower()

  @staticmethod
  ##
  # Gets the corresponding enum-object for specified type defined as
  # string in template route. Defaults to RocketPathVariableTypes.STR.
  #
  # @param  t   type in template route as string
  #
  # @return enum-object for specified type
  def FromStr(t: str):
    t = str(t).upper()
    return RocketPathVariableTypes.__dict__.get(t, RocketPathVariableTypes.STR)


##
# Named tuple for specifying a path-variable template in a template route.
#
# @param  Index   `int` -- Index of module after .split("/")
# @param  Class   `type` -- Represented python type of variable
# @param  Name    `str` -- Name/key of variable
class RocketPathVariable(NamedTuple):
  Index: int
  Class: type
  Name: str


##
# Class for storing an retrieving function-pointers corresponding to a
# specific HTTP Method.
class HttpApiMethods():

  ##
  # @var POSSIBLE_METHODS
  # All possible/existing HTTP methods.
  POSSIBLE_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]

  ##
  # @var FunctionsLookup
  # Dictionary for mapping HTTP methods to a function pointer
  FunctionsLookup: Dict[str, FunctionType]

  ##
  # Constructor
  def __init__(self) -> None:
    self.FunctionsLookup = {}

  ##
  # Maps a function-pointer to specific HTTP Method(s).
  #
  # @param  acceptedHttpMethods  list of HTTP Methods that are accepted
  # @param  functionPtr  function-pointer
  def Register(self, acceptedHttpMethods: List[str],
               functionPtr: FunctionType) -> None:
    for method in acceptedHttpMethods:
      # check if `method` is valid http-method
      if method in self.POSSIBLE_METHODS:
        # map function pointer to key `method`
        self.FunctionsLookup[method] = functionPtr
      else:
        # throw excpetion, if `method` is not a http-method
        raise NotSupportedError(f"unsupported rest-method: '{method}'")

  ##
  # Returns the function-pointer corresponding to HTTP request method.
  #
  # @return function-pointer for HTTP Method, None if invalid HTTP request
  # method
  def Get(self, httpFunctionType: str) -> Optional[FunctionType]:
    return self.FunctionsLookup.get(httpFunctionType)


##
# Defines a templated path object for RocketRouter to figure out the original
# templated path, position and type of path-variables and function pointers for
# specific HTTP method.
class RocketTemplatedPath():

  ##
  # @var TemplatedPathStr
  # Original templated path string from which object was built.
  TemplatedPathStr: str

  ##
  # @var TemplatedPathVariables
  # List of extracted path variables, with position, type and name.
  TemplatedPathVariables: List[RocketPathVariable]

  ##
  # @var HttpMethodsMap
  # Dictionary of HTTP methods mapped to corresponding function pointers.
  HttpMethodsMap: HttpApiMethods

  ##
  # Constructor.
  #
  # @param templatedPathStr  string that describes route template
  # @param templatedPathVariables  list of extracted vars from templatedPathStr
  # @param functionPtr  function-pointer
  # @param acceptedHttpMethods  list of HTTP Methods that are accepted
  def __init__(self, templatedPathStr: str,
               templatedPathVariables: List[RocketPathVariable],
               functionPtr: FunctionType,
               acceptedHttpMethods: List[str]) -> None:
    self.TemplatedPathVariables = templatedPathVariables
    self.TemplatedPathStr = templatedPathStr
    self.HttpMethodsMap = HttpApiMethods()
    self.HttpMethodsMap.Register(acceptedHttpMethods, functionPtr)


##
# Returned tuple on a specific path with mapped variables and function.
#
# @param  Vars  `Dict[str, Any]` -- Mapped variables from templated path
# @param  Function  `FunctionType` -- Function pointer
class RocketSpecificPath(NamedTuple):
  Vars: Dict[str, Any]
  Function: FunctionType


##
# Class is a superset of the flask library. flask is used to serve the API and
# also to handle the request via the request object, which flask provides. The
# RocketRouter class only replaces the standard routing of flask, with a more
# versatile regex router, than the default flask router.
class RocketRouter():

  ##
  # @var routes
  # Internal map for template-routes.
  routes: Dict[Pattern, RocketTemplatedPath]

  ##
  # Constructor
  def __init__(self) -> None:
    self.routes = {}

  ##
  # Registers a handler function for a specific template-route. Variables have
  # to be declared as "{name:type}" (supported types can be found in
  # RocketPathVariableTypes).
  #
  # @param  templatedPathStr   template path for route
  # @param  functionPtr  function that should be run on route-match
  # @param  acceptedHttpMethods  list of HTTP Methods that are accepted
  def Mount(self, templatedPathStr: str, functionPtr: FunctionType,
            acceptedHttpMethods: List[str]) -> None:
    # split route into individual modules
    modules = templatedPathStr.split("/")
    modules = list(filter(("").__ne__, modules))
    # initialize list for varibles found in path
    variables = []

    # convert variable modules to regex and save information about position,
    # type and name of variable in variables list.
    for index, mod in enumerate(modules):
      # check if module is variable
      if mod.startswith("{"):
        # save information about varibale in variables-list
        varname, vartype = tuple(mod[1:-1].split(":"))
        vartype = RocketPathVariableTypes.FromStr(vartype)
        variables.append(RocketPathVariable(index, vartype.value.t, varname))
        # convert variable-template to regex
        modules[index] = vartype.value.regex

    # convert whole path to single regex expression
    regex = re.compile("/".join(modules))
    # register route-template under regex in container 'routes'
    if self.routes.get(regex) is None:
      self.routes[regex] = RocketTemplatedPath(templatedPathStr, variables,
                                               functionPtr, acceptedHttpMethods)
    else:
      self.routes[regex].HttpMethodsMap.Register(acceptedHttpMethods,
                                                 functionPtr)

  ##
  # Will try to find a match for a given route in internal template-paths. If
  # none can be found, None will be returned. If a route has been found, a
  # RocketSpecificPath with the variables and function will be returned.
  #
  # @param  route   api path with variables set
  # @param  httpApiFunc   HTTP method that was used for request as string
  #
  # @return RocketSpecificPath for first parameter in tuple. If an error occurs,
  # second parameter will be set to an Error object of scheme
  # `Error(Msg, HttpStatus)`.
  def Match(self, route: str,
            httpApiFunc: str) -> Tuple[RocketSpecificPath, Error]:
    templates = []
    modules = route.split("/")
    variables = {}

    # get templates that match regex and path
    for regex, template in self.routes.items():
      if regex.match(route) is not None:
        templates.append(template)

    # only one template should be returned for a route. If more then one are
    # returned, raise RuntimeError. If none was found, return None for route.
    if len(templates) != 1:
      if len(templates) > 1:
        return None, Error("to many matched routes found",
                           HttpStatus.MULTIPLE_CHOICES)
      return None, Error("no matching routes could be found",
                         HttpStatus.NOT_FOUND)

    # rename templates[0] for easier writing
    template = templates[0]
    # map values for variables into dictionary (values are casted as represented
    # types)
    for var in template.TemplatedPathVariables:
      variables[var.Name] = var.Class(modules[var.Index])

    # check if function is supported by
    functionPtr = template.HttpMethodsMap.Get(httpApiFunc)
    if functionPtr is None:
      return None, Error("HTTP method is not allowed on this route",
                         HttpStatus.METHOD_NOT_ALLOWED)

    # return route object for specific route
    Io.Debug(f"    => Matched: ({functionPtr.__name__}) {httpApiFunc} "
             f"{template.TemplatedPathStr}")
    return RocketSpecificPath(variables, functionPtr), None

  ##
  # Prints detailed debug information on router.
  #
  # @example
  # ```{.sh}
  # 2022/04/20 08:53:07 (UTC) DEBUG    | Routes:
  # 2022/04/20 08:53:07 (UTC) DEBUG    |     - /hello/{name:str} GET,POST
  # 2022/04/20 08:53:07 (UTC) DEBUG    | Environment: "/pate-wapi"
  # 2022/04/20 08:53:07 (UTC) DEBUG    | Serving REST API at "/pate-wapi/Paperwrite/RocketRouter.py"
  # 2022/04/20 08:53:07 (UTC) DEBUG    | Mounting at http://0.0.0.0:4321/api/w
  # ```
  def PrintDebugInformation(self) -> None:
    host = AppContext.Config.Webserver.Host
    port = AppContext.Config.Webserver.Port
    apiPrefix = AppContext.Config.Webserver.ApiPrefix
    routesList = self.GetRoutesDetailed()

    Io.Debug("Routes:")
    for r in routesList:
      Io.Debug(f"    - {r}")
    Io.Debug(f"Environment: \"{os.getcwd()}\"")
    Io.Debug(f"Serving REST API at \"{os.path.abspath( __file__ )}\"")
    Io.Debug(f"Mounting at http://{host}:{port}{apiPrefix}")

  ##
  # Will return a list with templated path strings of all routes as strings,
  # that are currently stored inside the router.
  #
  # @return List of routes as string.
  def GetRoutes(self) -> List[str]:
    return [t.TemplatedPathStr for t in self.routes.values()]

  ##
  # Will return a list with templated path string of all routes, that are
  # currently stored inside the router, with their accepted REST method(s)
  # (divided by `,`) appended as strings (scheme:
  # `<Templated Path> <REST Methods>`).
  #
  # @return List of routes and their accepted HTTP method(s) as string.
  def GetRoutesDetailed(self) -> List[str]:
    results = []

    # iterate through routes
    for t in self.routes.values():
      # get all methods, for which the function-pointer is not None and
      # therefore accepted by the route
      methods = t.HttpMethodsMap.FunctionsLookup.keys()
      methods = ",".join(methods)
      # append combined string to results
      results.append(f"{t.TemplatedPathStr} {methods}")

    return results

  ##
  # Logs a REST-request to the command line with scheme
  # `<HTTP Method> <API Path> <HTTP Scheme>`.
  #
  # @example
  # ```
  # GET /hello/world http
  # ```
  def PrintDebugInformationOnRequest(self) -> None:
    Io.Debug(f"{request.method} {request.path} {request.scheme}")

  ##
  # Handles an API-route call with the specific path 'routePath' and will
  # return a valid flask response or abort inside the function. If the specific
  # path can not be found in the internal router-paths, an error 404 will be
  # sent to user.
  #
  # @param  routePath   api path with variables set
  #
  # @return Reponse from internal function from path.
  def HandleFunc(self, routePath: str, httpApiFunc: str) -> Response:
    # search for matching template-route in routes
    self.PrintDebugInformationOnRequest()
    route, err = self.Match(routePath, httpApiFunc)

    if err is not None:
      Io.Debug(f"    => Matching Error: {err.args[0]}")
      RespondWithError(err.args[1], err.args[0])

    # if route was found execute handler and pass variables
    return route.Function(**route.Vars)

  ##
  # Wrapper for BuildFlaskApiProvider on self object.
  #
  # @return Flask application of self
  #
  # @see
  #   - BuildFlaskApiProvider
  def Build(self) -> Flask:
    return BuildFlaskApiProvider(self)


##
# Capsules the RocketRouter inside a Flask application. All changes made to
# router object after built, will affect built Flask provider object.
#
# @param  router  router object from which provider should be built
# @return Flask application of router
def BuildFlaskApiProvider(router: RocketRouter) -> Flask:
  # create base flask provider object
  provider = Flask(__name__)
  # enable cors for flask
  CORS(provider)

  # root path supports all rest methods and just passes through the path after
  # the prefix (defined in config)
  @provider.route(f"{AppContext.Config.Webserver.ApiPrefix}/<path:__p>",
                  methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
  def __internal_ProviderRootPath(__p: str) -> Response:
    # passthrough to Router
    return router.HandleFunc(__p, request.method)

  # global error handler for flask.
  @provider.errorhandler(Exception)
  def __internal_ProviderErrorHandler(__ex: Exception) -> Response:
    # create json response with information on caught error
    status = HttpStatus.INTERNAL_SERVER_ERROR
    msg = {
        "success": False,
        "tod": datetime.now().isoformat(),  # time of discovery
        "error": {
            "type": __ex.__class__.__name__,
            "message": str(__ex),
            "http_name": status.Title(),
            "http_code": status.value
        }
    }
    # print debug information on caught error
    Io.Debug(f"    => Exeption: {__ex.__class__.__name__}")
    Io.Debug(f"        !> {str(__ex)}")
    response = CreateResponseJson(status, msg)

    Io.Error(f"{request.method} {request.path} {request.scheme}, "
             f"{request.remote_addr} - {status.value}")
    # TODO: add propagte_exceptions to configuration file
    # send error response with information to user
    return response

  # print general debug information on router, before return
  router.PrintDebugInformation()
  # return built provider
  return provider
