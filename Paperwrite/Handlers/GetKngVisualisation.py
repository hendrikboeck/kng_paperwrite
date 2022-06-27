import os
from flask import Response

from Paperwrite.Application import AppContext
from Paperwrite.Rest import CreateResponseHTML, HttpStatus


def GetKngVisualisation(kid: str) -> Response:
  path = os.path.join(AppContext.Store.Mutable, kid, "graph_visualisation.html")
  return CreateResponseHTML(HttpStatus.OK, path)
