import os
import json

from flask import Response
import numpy as np
from ampligraph.latent_features import ComplEx
from ampligraph.utils import save_model

from Paperwrite.Rest import CreateResponseJson, HttpStatus
from Paperwrite.Application import AppContext


def GetKngTrainModel(kid: str) -> Response:
  storeFolder = os.path.join(AppContext.Store.Mutable, kid)
  metadataPath = os.path.join(storeFolder, "metadata.json")

  with open(metadataPath, "r") as f:
    metadata = json.load(f)

  metadata["ai_models"] = "training..."

  with open(metadataPath, "w") as f:
    json.dump(metadata, f)

  model = ComplEx(batches_count=1, seed=555, epochs=200, k=1000)
  X = np.load(os.path.join(storeFolder, "raw_graph_data.npy"))
  model.fit(X)
  save_model(model, model_name_path=os.path.join(storeFolder, "complex.pkl"))

  metadata["ai_models"] = "ComplEx"

  with open(metadataPath, "w") as f:
    json.dump(metadata, f)

  return CreateResponseJson(HttpStatus.OK, {})