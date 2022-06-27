##
# @file
# @author Hendrik Boeck <hendrikboeck.dev@protonmail.com>
#
# @package   Paperwrite.Rest
# @namespace Paperwrite.Rest
#
# Package for working with RESTful applications.

# -- STL
from enum import Enum
from datetime import datetime
import os
from typing import Any, Dict, List, NoReturn
import io

# -- LIBRARY
from PIL.Image import Image
from flask import make_response, jsonify, abort, Response, send_file, request, render_template_string

from Paperwrite.PyAdditions import Io


##
# Enum of current HTTP codes from https://httpstatuses.com/
#
#  - *1xx* -- `Informational`
#  - *2xx* -- `Success`
#  - *3xx* -- `Redirection`
#  - *4xx* -- `Client Error`
#  - *5xx* -- `Server Error`
#
class HttpStatus(Enum):

  # 1xx -- INFORMATIONAL

  ##
  # *100* `Continue`
  #
  # The initial part of a request has been received and has not yet been
  # rejected by the server. The server intends to send a final response after
  # the request has been fully received and acted upon.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.2.1
  CONTINUE = 100

  ##
  # *101* `Switch Protocols`
  #
  # The server understands and is willing to comply with the client's request,
  # via the Upgrade header field, for a change in the application protocol being
  # used on this connection.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.2.2
  SWITCH_PROTOCOLS = 101

  ##
  # *102* `Processing`
  #
  # An interim response used to inform the client that the server has accepted
  # the complete request, but has not yet completed it.
  #
  # Source: https://tools.ietf.org/html/rfc2518#section-10.1
  PROCESSING = 102

  # 2xx -- SUCCESS

  ##
  # *200* `Success`
  #
  # The request has succeeded.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.3.1
  OK = 200

  ##
  # *201* `Created`
  #
  # The request has been fulfilled and has resulted in one or more new resources
  # being created.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.3.2
  CREATED = 201

  ##
  # *202* `Accepted`
  #
  # The request has been accepted for processing, but the processing has not
  # been completed. The request might or might not eventually be acted upon, as
  # it might be disallowed when processing actually takes place.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.3.3
  ACCEPTED = 202

  ##
  # *203* `Non-authoritative Information`
  #
  # The request was successful but the enclosed payload has been modified from
  # that of the origin server's 200 OK response by a transforming proxy.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.3.4
  NON_AUTORITATIVE_INFORMATION = 203

  ##
  # *204* `No Content`
  #
  # The server has successfully fulfilled the request and that there is no
  # additional content to send in the response payload body.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.3.5
  NO_CONTENT = 204

  ##
  # *205* `Reset Content`
  #
  # The server has fulfilled the request and desires that the user agent reset
  # the "document view", which caused the request to be sent, to its original
  # state as received from the origin server.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.3.6
  RESET_CONTENT = 205

  ##
  # *206* `Partial Content`
  #
  # The server is successfully fulfilling a range request for the target
  # resource by transferring one or more parts of the selected representation
  # that correspond to the satisfiable ranges found in the request's Range
  # header field.
  #
  # Source: https://tools.ietf.org/html/rfc7233#section-4.1
  PARTIAL_CONTENT = 206

  ##
  # *207* `Multi-Status`
  #
  # A Multi-Status response conveys information about multiple resources in
  # situations where multiple status codes might be appropriate.
  #
  # Source: https://tools.ietf.org/html/rfc4918#section-13
  MULTI_STATUS = 207

  ##
  # *208* `Already Reported`
  #
  # Used inside a DAV: propstat response element to avoid enumerating the
  # internal members of multiple bindings to the same collection repeatedly.
  #
  # Source: https://tools.ietf.org/html/rfc5842#section-7.1
  ALREADY_REPORTED = 208

  ##
  # *226* `IM Used`
  #
  # The server has fulfilled a GET request for the resource, and the response is
  # a representation of the result of one or more instance-manipulations applied
  # to the current instance.
  #
  # Source: https://tools.ietf.org/html/rfc3229#section-10.4.1
  IM_USED = 226

  # 3xx -- REDIRECTION

  ##
  # *300* `Multiple Choices`
  #
  # The target resource has more than one representation, each with its own more
  # specific identifier, and information about the alternatives is being
  # provided so that the user (or user agent) can select a preferred
  # representation by redirecting its request to one or more of those
  # identifiers.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.4.1
  MULTIPLE_CHOICES = 300

  ##
  # *301* `Moved Permanently`
  #
  # The target resource has been assigned a new permanent URI and any future
  # references to this resource ought to use one of the enclosed URIs.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.4.2
  MOVED_PERMANENTLY = 301

  ##
  # *302* `Found`
  #
  # The target resource resides temporarily under a different URI. Since the
  # redirection might be altered on occasion, the client ought to continue to
  # use the effective request URI for future requests.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.4.3
  FOUND = 302

  ##
  # *303* `See Other`
  #
  # The server is redirecting the user agent to a different resource, as
  # indicated by a URI in the Location header field, which is intended to
  # provide an indirect response to the original request.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.4.4
  SEE_OTHER = 303

  ##
  # *304* `Not Modified`
  #
  # A conditional GET or HEAD request has been received and would have resulted
  # in a 200 OK response if it were not for the fact that the condition
  # evaluated to false.
  #
  # Source: https://tools.ietf.org/html/rfc7232#section-4.1
  NOT_MODIFIED = 304

  ##
  # *305* `Use Proxy`
  #
  # Defined in a previous version of this specification and is now deprecated,
  # due to security concerns regarding in-band configuration of a proxy.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.4.5
  USE_PROXY = 305

  ##
  # *307* `Temporary Redirect`
  #
  # The target resource resides temporarily under a different URI and the user
  # agent MUST NOT change the request method if it performs an automatic
  # redirection to that URI.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.4.7
  TEMPORARY_REDIRECT = 307

  ##
  # *308* `Permanent Redirect`
  #
  # The target resource has been assigned a new permanent URI and any future
  # references to this resource ought to use one of the enclosed URIs.
  #
  # Source: https://tools.ietf.org/html/rfc7538#section-3
  PERMANENT_REDIRECT = 308

  # 4xx -- CLIENT ERROR

  ##
  # *400* `Bad Request`
  #
  # The server cannot or will not process the request due to something that is
  # perceived to be a client error (e.g., malformed request syntax, invalid
  # request message framing, or deceptive request routing).
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.5.1
  BAD_REQUEST = 400

  ##
  # *401* `Unauthorized`
  #
  # The request has not been applied because it lacks valid authentication
  # credentials for the target resource.
  #
  # Source: https://tools.ietf.org/html/rfc7235#section-3.1
  UNAUTHORIZED = 401

  ##
  # *402* `Payment Required`
  #
  # Reserved for future use.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.5.2
  PAYMENT_REQUIRED = 402

  ##
  # *403* `Forbidden`
  #
  # The server understood the request but refuses to authorize it.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.5.3
  FORBIDDEN = 403

  ##
  # *404* `Not Found`
  #
  # The origin server did not find a current representation for the target
  # resource or is not willing to disclose that one exists.
  #
  # Source: https://tools.ietf.org/html/rfc7234#section-4.2.2
  NOT_FOUND = 404

  ##
  # *405* `Method Not Allowed`
  #
  # The method received in the request-line is known by the origin server but
  # not supported by the target resource.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.5.5
  METHOD_NOT_ALLOWED = 405

  ##
  # *406* `Not Acceptable`
  #
  # The target resource does not have a current representation that would be
  # acceptable to the user agent, according to the proactive negotiation header
  # fields received in the request, and the server is unwilling to supply a
  # default representation.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.5.6
  NOT_ACCEPTABLE = 406

  ##
  # *407* `Proxy Authentication Required`
  #
  # Similar to 401 Unauthorized, but it indicates that the client needs to
  # authenticate itself in order to use a proxy.
  #
  # Source: https://tools.ietf.org/html/rfc7235#section-3.2
  PROXY_AUTHENTICATION_REQUIRED = 407

  ##
  # *408* `Request Timeout`
  #
  # The server did not receive a complete request message within the time that
  # it was prepared to wait.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.5.7
  REQUEST_TIMEOUT = 408

  ##
  # *409* `Conflict`
  #
  # The request could not be completed due to a conflict with the current state
  # of the target resource. This code is used in situations where the user might
  # be able to resolve the conflict and resubmit the request.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.5.8
  CONFLICT = 409

  ##
  # *410* `Gone`
  #
  # The target resource is no longer available at the origin server and that
  # this condition is likely to be permanent.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.5.9
  GONE = 410

  ##
  # *411* `Length Required`
  #
  # The server refuses to accept the request without a defined Content-Length.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.5.10
  LENGTH_REQUIRED = 411

  ##
  # *412* `Precondition Failed`
  #
  # One or more conditions given in the request header fields evaluated to false
  # when tested on the server.
  #
  # Source: https://tools.ietf.org/html/rfc7232#section-4.2
  PRECONDITION_FAILED = 412

  ##
  # *413* `Payload Too Large`
  #
  # The server is refusing to process a request because the request payload is
  # larger than the server is willing or able to process.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.5.11
  PAYLOAD_TOO_LARGE = 413

  ##
  # *414* `Request-URI Too Long`
  #
  # The server is refusing to service the request because the request-target is
  # longer than the server is willing to interpret.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.5.12
  REQUEST_URI_TOO_LONG = 414

  ##
  # *415* `Unsupported Media Type`
  #
  # The origin server is refusing to service the request because the payload is
  # in a format not supported by this method on the target resource.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.5.13
  UNSUPPORTED_MEDIA_TYPE = 415

  ##
  # *416* `Requested Range Not Satisfiable`
  #
  # None of the ranges in the request's Range header field overlap the current
  # extent of the selected resource or that the set of ranges requested has been
  # rejected due to invalid ranges or an excessive request of small or
  # overlapping ranges.
  #
  # Source: https://tools.ietf.org/html/rfc7233#section-4.4
  REQUESTED_RANGE_NOT_SATISFIABLE = 416

  ##
  # *417* `Expectation Failed`
  #
  # The expectation given in the request's Expect header field could not be met
  # by at least one of the inbound servers.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.5.14
  EXPECTATION_FAILED = 417

  ##
  # *418* `I'm a teapot`
  #
  # Any attempt to brew coffee with a teapot should result in the error code
  # "418 I'm a teapot". The resulting entity body MAY be short and stout.
  #
  # Source: https://tools.ietf.org/html/rfc2324#section-2.3.2
  I_M_A_TEAPOT = 418

  ##
  # *421* `Misdirected Request`
  #
  # The request was directed at a server that is not able to produce a response.
  # This can be sent by a server that is not configured to produce responses for
  # the combination of scheme and authority that are included in the request
  # URI.
  #
  # Source: https://tools.ietf.org/html/rfc7540#section-9.1.2
  MISDIRECTED_REQUEST = 421

  ##
  # *422* `Unprocessable Entity`
  #
  # The server understands the content type of the request entity (hence a 415
  # Unsupported Media Type status code is inappropriate), and the syntax of the
  # request entity is correct (thus a 400 Bad Request status code is
  # inappropriate) but was unable to process the contained instructions.
  #
  # Source: https://tools.ietf.org/html/rfc4918#section-11.2
  UNPROCESSABLE_ENTITY = 422

  ##
  # *423* `Locked`
  #
  # The source or destination resource of a method is locked.
  #
  # Source: https://tools.ietf.org/html/rfc4918#section-11.3
  LOCKED = 423

  ##
  # *424* `Failed Dependency`
  #
  # The method could not be performed on the resource because the requested action
  # depended on another action and that action failed.
  #
  # Source: https://tools.ietf.org/html/rfc4918#section-11.4
  FAILED_DEPENDENCY = 424

  ##
  # *426* `Upgrade Required`
  #
  # The server refuses to perform the request using the current protocol but
  # might be willing to do so after the client upgrades to a different protocol.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.5.15
  UPGRADE_REQUIRED = 426

  ##
  # *428* `Precondition Required`
  #
  # The origin server requires the request to be conditional.
  #
  # Source: https://tools.ietf.org/html/rfc6585#section-3
  PRECONDITION_REQUIRED = 428

  ##
  # *429* `Too Many Requests`
  #
  # The user has sent too many requests in a given amount of time ("rate
  # limiting").
  #
  # Source: https://tools.ietf.org/html/rfc6585#section-4
  TOO_MANY_REQUESTS = 429

  ##
  # *431* `Request Header Fields Too Large`
  #
  # The server is unwilling to process the request because its header fields are
  # too large. The request MAY be resubmitted after reducing the size of the
  # request header fields.
  #
  # Source: https://tools.ietf.org/html/rfc6585#section-5
  REQUEST_HEADER_FIELDS_TOO_LARGE = 431

  ##
  # *444* `Connection Closed Without Response`
  #
  # A non-standard status code used to instruct nginx to close the connection
  # without sending a response to the client, most commonly used to deny
  # malicious or malformed requests.
  #
  # Source: https://nginx.org/en/docs/http/ngx_http_rewrite_module.html#return
  CONNECTION_CLOSED_WITHOUT_RESPONSE = 444

  ##
  # *451* `Unavailable For Legal Reasons`
  #
  # The server is denying access to the resource as a consequence of a legal
  # demand.
  #
  # Source: https://tools.ietf.org/html/rfc7725
  UNAVAILABLE_FOR_LEGAL_REASONS = 451

  ##
  # *499* `Client Closed Request`
  #
  # A non-standard status code introduced by nginx for the case when a client
  # closes the connection while nginx is processing the request.
  #
  # Source: http://lxr.nginx.org/source/src/http/ngx_http_request.h#0120
  CLIENT_CLOSED_REQUEST = 499

  # 5xx -- SERVER ERROR

  ##
  # *500* `Internal Server Error`
  #
  # The server encountered an unexpected condition that prevented it from
  # fulfilling the request.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.6.1
  INTERNAL_SERVER_ERROR = 500

  ##
  # *501* `Not Implemented`
  #
  # The server does not support the functionality required to fulfill the
  # request.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.6.2
  NOT_IMPLEMENTED = 501

  ##
  # *502* `Bad Gateway`
  #
  # The server, while acting as a gateway or proxy, received an invalid response
  # from an inbound server it accessed while attempting to fulfill the request.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.6.3
  BAD_GATEWAY = 502

  ##
  # *503* `Service Unavailable`
  #
  # The server is currently unable to handle the request due to a temporary
  # overload or scheduled maintenance, which will likely be alleviated after
  # some delay.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.6.4
  SERVICE_UNAVAILABLE = 503

  ##
  # *504* `Gateway Timeout`
  #
  # The server, while acting as a gateway or proxy, did not receive a timely
  # response from an upstream server it needed to access in order to complete
  # the request.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.6.5
  GATEWAY_TIMEOUT = 504

  ##
  # *505* `HTTP Version Not Supported`
  #
  # The server does not support, or refuses to support, the major version of
  # HTTP that was used in the request message.
  #
  # Source: https://tools.ietf.org/html/rfc7231#section-6.6.6
  HTTP_VERSION_NOT_SUPPORTED = 505

  ##
  # *506* `Variant Also Negotiates`
  #
  # The server has an internal configuration error: the chosen variant resource
  # is configured to engage in transparent content negotiation itself, and is
  # therefore not a proper end point in the negotiation process.
  #
  # Source: https://tools.ietf.org/html/rfc2295#section-8.1
  VARIANT_ALSO_NEGOTIATES = 506

  ##
  # *507* `Insufficient Storage`
  #
  # The method could not be performed on the resource because the server is
  # unable to store the representation needed to successfully complete the
  # request.
  #
  # Source: https://tools.ietf.org/html/rfc4918#section-11.5
  INSUFFICIENT_STORAGE = 507

  ##
  # *508* `Loop Detected`
  #
  # The server terminated an operation because it encountered an infinite loop
  # while processing a request with "Depth: infinity". This status indicates
  # that the entire operation failed.
  #
  # Source: https://tools.ietf.org/html/rfc5842#section-7.2
  LOOP_DETECTED = 508

  ##
  # *510* `Not Extended`
  #
  # The policy for accessing the resource has not been met in the request. The
  # server should send back all the information necessary for the client to
  # issue an extended request.
  #
  # Source: https://tools.ietf.org/html/rfc2774#section-7
  NOT_EXTENDED = 510

  ##
  # *511* `Network Authentication Required`
  #
  # The client needs to authenticate to gain network access.
  #
  # Source: https://tools.ietf.org/html/rfc6585#section-6
  NETWORK_AUTHENTICATION_REQUIRED = 511

  ##
  # *599* `Network Connect Timeout Error`
  #
  # This status code is not specified in any RFCs, but is used by some HTTP
  # proxies to signal a network connect timeout behind the proxy to a client in
  # front of the proxy.
  #
  # Source: unkown?
  NETWORK_CONNECT_TIMEOUT_ERROR = 599

  def Title(self) -> str:
    return self.name.replace("_", " ").title()


##
# Will exit the function with http-status code and return a json with embedded
# "error"-field and optional payload defined by *args and **kwargs:
#
# ~~~{.py}
# {
#   "error": "...error",
#   ...args,
#   ...kwargs,
# }
# ~~~
#
# @param  status  HTTP status code
# @param  error   error message to return
# @param  *args   variable length argument list for aditional fields in json
# @param  **kwargs  arbitrary keyword arguments for aditional fields in json
#
# @return   calls internally flask.abort
def RespondWithError(status: HttpStatus, error: str, *args: List[Any],
                     **kwargs: Dict[str, Any]) -> NoReturn:
  Io.Debug(f"    => Outcome: {status.value}, {status.Title()}")
  msg = {
      "tod": datetime.now().isoformat(),  # time of discovery
      "success": False,
      "error": {
          "type": "HTTPException",
          "message": error,
          "http_name": status.Title(),
          "http_code": status.value
      }
  }

  logFunc = Io.Info
  if status.value >= 500:
    logFunc = Io.Error
  elif status.value >= 400:
    logFunc = Io.Warning
  logFunc(
      f"{request.method} {request.path} {request.scheme}, {request.remote_addr}"
      f" - {status.value}")
  abort(make_response(jsonify(*args, msg, **kwargs), status.value))


##
# Creates a flask.Response as json with http-status code.
#
# @param  status  HTTP status code
# @param  *args   variable length argument list for aditional fields in json
# @param  **kwargs  arbitrary keyword arguments for aditional fields in json
#
# @return   json as flask.Response with HTTP status
def CreateResponseJson(status: HttpStatus, *args, **kwargs) -> Response:
  Io.Debug(f"    => Outcome: {status.value}, {status.Title()}")
  return make_response(jsonify(*args, **kwargs), status.value)


##
# Creates a flask.Response as jpeg with http-status code from a PIL image.
#
# @param  status  HTTP status code
# @param  image   PIL image to be send
#
# @return   image as jpeg (80%) as flask.Reponse with HTTP status
def CreateResponsePILImage(status: HttpStatus, image: Image) -> Response:
  # create buffer for saving image to
  bbuf = io.BytesIO()
  # save image to buffer
  image.save(bbuf, 'JPEG', quality=80)
  # set stream position to beginning for flask reading
  bbuf.seek(0)
  # create Response from buffer
  Io.Debug(f"    => Outcome: {status.value}, {status.Title()}")
  return make_response(send_file(bbuf, mimetype='image/jpeg'), status.value)


def CreateResponseHTML(status: HttpStatus, path: str) -> Response:
  Io.Debug(f"    => Outcome: {status.value}, {status.Title()}")
  with open(path, "r") as f:
    data = f.read()
  return make_response(render_template_string(data), status.value)


##
# Validates a dictionary based on a protype, which describes the types and
# existence for keys and values in dictionary.
#
# @param  body  JSON-dictionary parsed from body of a REST-request
# @param  proto dictionary containing types an templates for body
def ValidateRequestJson(body: Dict[str, Any], proto: Dict[str, Any]) -> None:
  # create a NULL object for identifying, when the 'get' returns a true
  # null/None value or does not find the key
  NULL = object()

  # iterate through prototype dictionary
  for key, t in proto.items():
    # get value for key in body
    val = body.get(key, NULL)

    # check if key is present in body, if key is missing, issue a error-message
    if val == NULL:
      RespondWithError(HttpStatus.BAD_REQUEST, f"key '{key}' is missing")

    # if value for t is a dictionary, check if value in body is a dictionary as
    # well and then recurse through sub-dictionary and check it's values as well
    if isinstance(t, dict):
      # check type is dictionary
      if not isinstance(val, dict):
        RespondWithError(
            HttpStatus.BAD_REQUEST,
            f"found type {type(val)}, expected type {dict} for key '{key}'")
      # validate sub-dictionary as well
      ValidateRequestJson(val, t)
    # if value for t is list, check length and type of array. If length or type
    # does not match return an error-message to the user.
    elif isinstance(t, list):
      # check type type of list
      if not isinstance(val[0], t[1]):
        RespondWithError(
            HttpStatus.BAD_REQUEST,
            f"found type {type(val)}, expected array-type {t[1]} for key "
            f"'{key}'")
      else:
        # check if value-array has correct length (0 eq infinty)
        if t[0] != 0 and len(val) != t[0]:
          RespondWithError(HttpStatus.BAD_REQUEST,
                           f"array for key '{key}' must be of lenth {t}")
    # if value for t is type, check if value in body is instance of this type;
    # if types do not match issue an error-message
    elif isinstance(t, type):
      # check if value is of type t
      if not isinstance(val, t):
        RespondWithError(
            HttpStatus.BAD_REQUEST,
            f"found type {type(val)}, expected type {t} for key '{key}'")
