import os
import json

from flask import Response

from Paperwrite.Rest import CreateResponseJson, HttpStatus
from Paperwrite.Application import AppContext


def GetKngList() -> Response:
  kngs = os.listdir(AppContext.Store.Mutable)

  results = []
  for kng in kngs:
    with open(os.path.join(AppContext.Store.Mutable, kng,
                           "metadata.json")) as f:
      data = json.load(f)
    results.append({"kid": kng, **data})

  return CreateResponseJson(HttpStatus.OK, results)
