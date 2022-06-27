import os
import asyncio

import spacy
import numpy as np
from flask import Response, request
from ampligraph.utils import restore_model

from Paperwrite.Application import AppContext
from Paperwrite.PyAdditions import Io
from Paperwrite.Rest import CreateResponseJson, HttpStatus
from Paperwrite.Handlers.PostKngCreate import GetTuple


def PostKngPredict(kid: str) -> Response:
  modelPath = os.path.join(AppContext.Store.Mutable, kid, "complex.pkl")
  model = restore_model(modelPath)
  content = request.get_json(silent=True)
  nlp = spacy.load("en_core_web_sm")
  asyncLoop = asyncio.new_event_loop()
  tpl = asyncLoop.run_until_complete(GetTuple(content["sentence"], nlp))
  Io.Debug(f"   => Search tuples: {tpl}")

  try:
    result = model.predict(np.asarray(tpl))
    return CreateResponseJson(HttpStatus.OK, {"predit_val": result})
  except Exception:
    return CreateResponseJson(HttpStatus.BAD_REQUEST, {"predit_val": "only use existing nodes"})

