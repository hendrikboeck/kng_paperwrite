import os
import json

from flask import Response

from Paperwrite.Rest import CreateResponseJson, HttpStatus
from Paperwrite.Application import AppContext


def GetKngDetails(kid: str) -> Response:
  with open(os.path.join(AppContext.Store.Mutable, kid, "metadata.json")) as f:
    metadata = json.load(f)

  additionalData = {}
  if metadata.get("ai_models") is None:
    additionalData["ai_models"] = "none"

  result = {
      "kid": kid,
      **additionalData,
      **metadata,
  }
  return CreateResponseJson(HttpStatus.OK, result)