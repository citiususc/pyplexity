# Pyplexity

This package provides a simple interface to apply perplexity filters to any document. A possible use case for this technology could be the removal of boilerplate. 
Furthermore, it provides a WARC and HTML bulk processor, with distributed capabilities.

![](imgs/perpl.PNG)

## Models

## Installation process

## Usage example

Process a folder containing a dataset using a trigrams model.
```
poetry build
pip3 install dist/pyplexity-0.1.31-py3-none-any.whl
pyplexity bulk-perplexity --perpl-model ../../clueweb-b13-rawtext2/trigrams_bnc.st --perpl-limit 8000.0 \ 
    --trigrams --base-dir ./cleaned_webkb --output-dir ./perpl_filtered_webkb
```

## Distributed mode (cluster)


