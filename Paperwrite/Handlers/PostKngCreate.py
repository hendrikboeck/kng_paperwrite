# -- STL
import json
import os
import uuid
import shutil
import re
import asyncio
from typing import List
from datetime import datetime

# -- LIBRARY
import tqdm
import tqdm.asyncio
import numpy as np
import spacy
from spacy.matcher import Matcher
from spacy.lang.en import English
from spacy.language import Language
from spacy.tokens import Span
from flask import Response, request
from tika import parser
from pyvis.network import Network

# -- PROJECT
from Paperwrite.Application import AppContext
from Paperwrite.Rest import CreateResponseJson, HttpStatus
from Paperwrite.PyAdditions.Io import CLI_FORMATTER


async def GetEntities(sentence: str, nlp: Language) -> List[str]:
  entity1 = ""
  entity2 = ""

  previousTokenDependency = ""  # dependency tag of previous token in the sentence
  previousTokenText = ""  # previous token in the sentence

  prefix = ""
  modifier = ""

  for token in nlp(sentence):
    # if token is a punctuation mark then move on to the next token
    if token.dep_ != "punct":
      # check: token is a compound word or not
      if token.dep_ == "compound":
        prefix = token.text
        # if the previous word was also a 'compound' then add the current word to it
        if previousTokenDependency == "compound":
          prefix = previousTokenText + " " + token.text

      # check: token is a modifier or not
      if token.dep_.endswith("mod") == True:
        modifier = token.text
        # if the previous word was also a 'compound' then add the current word to it
        if previousTokenDependency == "compound":
          modifier = previousTokenText + " " + token.text

      if token.dep_.find("subj") == True:
        entity1 = modifier + " " + prefix + " " + token.text
        prefix = ""
        modifier = ""
        previousTokenDependency = ""
        previousTokenText = ""

      if token.dep_.find("obj") == True:
        entity2 = modifier + " " + prefix + " " + token.text

      # update variables
      previousTokenDependency = token.dep_
      previousTokenText = token.text

  return [entity1.strip(), entity2.strip()]


async def GetRelation(sentence: str, nlp: Language) -> str:
  doc = nlp(sentence)
  matcher = Matcher(nlp.vocab)
  pattern = [{
      'DEP': 'ROOT'
  }, {
      'DEP': 'prep',
      'OP': "?"
  }, {
      'DEP': 'agent',
      'OP': "?"
  }, {
      'POS': 'ADJ',
      'OP': "?"
  }]

  matcher.add("matching_1", [pattern])

  matches = matcher(doc)
  k = len(matches) - 1

  if k >= 0:
    span = doc[matches[k][1]:matches[k][2]]
    return span.text
  else:
    return "undefined"


async def GetTuple(sentence: str, nlp: Language) -> List[str]:
  entity1, entity2 = await GetEntities(sentence, nlp)
  relation = await GetRelation(sentence, nlp)

  return [entity1, relation, entity2]


async def GetTuplesAsyncHelper(progressDescription: str, sentences: List[Span],
                               nlp: Language) -> List[List[str]]:
  return [
      await GetTuple(s.text.strip(), nlp)
      async for s in tqdm.asyncio.tqdm(sentences, desc=progressDescription)
  ]


def PostKngCreate(kid: str) -> Response:
  # create upload id
  uploadId = uuid.uuid4().hex
  uploadFolder = os.path.join(AppContext.Store.Temporary, uploadId)
  storageFolder = os.path.join(AppContext.Store.Mutable, kid)
  os.makedirs(storageFolder, exist_ok=True)
  os.makedirs(uploadFolder, exist_ok=True)

  # get source files from
  files = request.files.getlist("files[]")
  paths = []
  knowledgeBase = []

  for f in files:
    path = os.path.join(uploadFolder, f.filename)
    f.save(path)
    paths.append(path)
    knowledgeBase.append(f.filename)

  sents = []

  nlp = English()
  nlp.add_pipe("sentencizer")
  for p in paths:
    raw = parser.from_file(p)
    textIn = raw["content"]

    # cleanup input
    cleanSourcePattern = r"\[[a-zA-Z\.\s]+,[\s\d]+\]"
    sourcePattern = r"\[[\w,\.\s?]+\]"
    singleLinePattern = r"\n{2}.+\n{2}"

    textIn = re.sub(singleLinePattern, "", textIn)
    textIn = textIn.replace("-\n", "")
    textIn = textIn.replace("\n", " ")
    refs = re.findall(cleanSourcePattern, textIn)
    textIn = re.sub(sourcePattern, "", textIn)

    doc = nlp(textIn)
    sents.extend([i for i in doc.sents])

  nlp = spacy.load("en_core_web_sm")
  desc = f"{CLI_FORMATTER.GetPrefix('DEBUG')}    => Building KNG"
  asyncLoop = asyncio.new_event_loop()
  data = asyncLoop.run_until_complete(GetTuplesAsyncHelper(desc, sents, nlp))
  kngArray = []

  for kngSet in np.asarray(data):
    for val in kngSet:
      val = val.replace("\n", " ").replace("\t", " ").replace("\r", " ")
      val = " ".join(val.split())
    if not ("" in kngSet or "undefined" in kngSet):
      kngArray.append(kngSet)

  for r in refs:
    kngArray.append(["Paper", "refrences", str(r)])

  kngNpArray = np.asarray(kngArray)
  storePath = os.path.join(storageFolder, "raw_graph_data.npy")
  np.save(storePath, kngNpArray)

  metadata = {
      "knowledge_base": knowledgeBase,
      "created": str(datetime.now()),
      "size": len(kngNpArray)
  }
  metadataPath = os.path.join(storageFolder, "metadata.json")
  with open(metadataPath, "w") as f:
    json.dump(metadata, f, indent=2)

  encapsuledKngNpArray = []
  for kngSet in kngNpArray:
    encapsuledKngNpArray.append(
        [f"\"{kngSet[0]}\"", f"\"{kngSet[1]}\"", f"\"{kngSet[2]}\""])
  encapsuledKngNpArray = np.asarray(encapsuledKngNpArray)

  net = Network(height="100%",
                width="100%",
                bgcolor='#141519',
                font_color='white',
                directed=True)
  for kngSet in kngNpArray:
    net.add_node(kngSet[0], label=kngSet[0])
    net.add_node(kngSet[2], label=kngSet[2])
    net.add_edge(kngSet[0], kngSet[2], label=kngSet[1])
  net.toggle_drag_nodes(False)
  net.save_graph(os.path.join(storageFolder, "graph_visualisation.html"))

  shutil.rmtree(uploadFolder)
  return CreateResponseJson(HttpStatus.OK, {"status": "ok"})
