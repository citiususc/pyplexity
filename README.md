# Pyplexity

This package provides a simple interface to apply perplexity filters to any document. A possible use case for this technology could be the removal of boilerplate. 
Furthermore, it provides a WARC and HTML bulk processor, with distributed capabilities.

![](imgs/perpl.PNG)

## Models
| Model | RAM usage | File size | Performance |
| --- | --- | --- | --- | 
| bigrams-bnc | 5GB | 600MB | x |
| bigrams-cord19 | 2GB | 230MB | x |

## Installation process
```
python3 -m pip install pyplexity
```
## Usage example

### Compute perplexity from console
Command "perplexity". By default, bigrams-bnc. Argument "--model bigrams-bnc" changes model. 

```
citius@pc:~$ pyplexity perplexity "this is normal text"
downloading: 100%|##########| 660M/660M [00:11<00:00, 59.0MiB/s]
Loading model... Done.
1844.85540669094
citius@pc:~$ pyplexity perplexity "this is normal HTML PAGE BOI%& 678346 NOR  text"
Loading model... Done.
44787.99199563819
```

### Compute perplexity from console


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
