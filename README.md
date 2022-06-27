## Installation

With GPU
```
docker build -t local/ppw:latest -f - . < Dockerfile.Gpu
docker run -d --name=ppw --gpus all -p 44777:44777 -v $PWD/store/:/store -v $PWD/ppw.yml:/ppw.yml local/ppw:latest
cd frontend
yarn install
yarn add serve
yarn build && serve build
```

With CPU
```
docker build -t local/ppw:latest -f - . < Dockerfile.Cpu
docker run -d --name=ppw -p 44777:44777 -v $PWD/store/:/store -v $PWD/ppw.yml:/ppw.yml local/ppw:latest
cd frontend
yarn install
yarn add serve
yarn build && serve build
```

## Sources
 - https://docs.ampligraph.org/en/1.2.0/index.html
 - https://spacy.io/
 - https://ieeexplore.ieee.org/abstract/document/8999622
 - https://neo4j.com/blog/text-to-knowledge-graph-information-extraction-pipeline/
 - https://drops.dagstuhl.de/opus/volltexte/2021/14555/pdf/OASIcs-LDK-2021-19.pdf
 - https://medium.com/swlh/text-to-knowledge-graph-683002cde6e0