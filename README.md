# Pyplexity

This package provides a simple interface to apply perplexity filters to any document. A possible use case for this technology could be the removal of boilerplate. 
Furthermore, it provides a WARC and HTML bulk processor, with distributed capabilities.

![](imgs/perpl.PNG)

## Models

## Installation process

## Usage example

Process a folder containing a dataset using a trigrams model.


## Distributed mode (cluster)

## Building the package

```
git clone https://github.com/citiususc/pyplexity && cd pyplexity
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
source $HOME/.poetry/env
poetry build
pip3 install dist/pyplexity-X.X.X-py3-none-any.whl
```
