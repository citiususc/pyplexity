# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyplexity', 'pyplexity.dataset_processor']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.0.2,<3.0.0',
 'cached-path>=1.0.2,<2.0.0',
 'html5lib>=1.1,<2.0',
 'lxml>=4.7.1,<5.0.0',
 'memory-tempfile>=2.2.3,<3.0.0',
 'nltk>=3.6.7,<4.0.0',
 'pandas>=1.1.5,<2.0.0',
 'storable>=1.2.4,<2.0.0',
 'typer[all]>=0.4.0,<0.5.0',
 'warcio>=1.7.4,<2.0.0']

entry_points = \
{'console_scripts': ['pyplexity = pyplexity.__main__:app']}

setup_kwargs = {
    'name': 'pyplexity',
    'version': '0.1.35',
    'description': 'Perplexity filter for documents and bulc HTML and WARC boilerplate removal.',
    'long_description': '# Pyplexity\n\nThis package provides a simple interface to apply perplexity filters to any document. A possible use case for this technology could be the removal of boilerplate. \nFurthermore, it provides a WARC and HTML bulk processor, with distributed capabilities.\n\n![](imgs/perpl.PNG)\n\n## Models\nMemory intensive but does not scale on CPU. \n| Model | RAM usage | Download size | Performance |\n| --- | --- | --- | --- | \n| bigrams-cord19 | 2GB | 230MB | x |\n| bigrams-bnc | 5GB | 660MB | x |\n| trigrams-cord19 | 6,6GB | 1GB | x |\n| trigrams-bnc | 14GB | 2,2GB | x |\n\n## Installation process\n```\npython3 -m pip install pyplexity\n```\n## Usage example\n\n### Compute perplexity from console\nCommand "perplexity". By default, bigrams-bnc. Argument "--model bigrams-bnc" changes model. \nDocumentation:\n```\ncitius@pc:~$ pyplexity perplexity --help\nUsage: pyplexity perplexity [OPTIONS] TEXT\n\nArguments:\n  TEXT  [required]\n\nOptions:\n  --model TEXT  [default: bigrams-bnc]\n  --help        Show this message and exit.\n```\nBy default, models are stored in ~/.cache/cached_path/, as per cached-path package documentation. Example:\n```\ncitius@pc:~$ pyplexity perplexity "this is normal text"\ndownloading: 100%|##########| 660M/660M [00:11<00:00, 59.0MiB/s]\nLoading model... Done.\n1844.85540669094\ncitius@pc:~$ pyplexity perplexity "this is normal HTML PAGE BOI%& 678346 NOR  text"\nLoading model... Done.\n44787.99199563819\n```\n### Bulk perplexity computation and cleaning of a directory\nDocumentation:\n```\ncitius@pc:~$ pyplexity bulk-perplexity --help\nUsage: pyplexity bulk-perplexity [OPTIONS] INPUT_DIR\n\nArguments:\n  INPUT_DIR  [required]\n\nOptions:\n  --output-dir TEXT                [default: out_dir]\n  --model TEXT                     [default: bigrams-bnc]\n  --perpl-limit FLOAT              [default: 8000.0]\n  --warc-input / --no-warc-input   [default: no-warc-input]\nDistributed computing options:\n  --distributed / --no-distributed [default: no-distributed]\n  --n-workers INTEGER              [default: 1]\n  --node INTEGER                   [default: 1]\n  --port INTEGER                   [default: 8866]\n  --help                           Show this message and exit.\n```\nWe will explain the distributed computing capabilities later. Input directory is allowed to have recursive subdirectories with files. It can process both WARC and raw text files. WARC containers and HTML files should have been previously tag-cleaned with the command below. Example:\n```\ncitius@pc:~$ pyplexity bulk-perplexity ./out_dir/ --output-dir cleaned_files --model bigrams-cord19\ndownloading: 100%|##########| 233M/233M [00:03<00:00, 63.3MiB/s] \nLoading model... Done.\nComputed 1124 files in 0:00:01.905390.\n```\n\n### Perform HTML tag cleaning of a directory\nDocumentation:\n```\ncitius@pc:~$ pyplexity tag-remover --help\nUsage: pyplexity tag-remover [OPTIONS] BASE_DIR\n\nArguments:\n  BASE_DIR  [required]\n\nOptions:\n  --output-dir TEXT                [default: out_dir]\n  --warc-input / --no-warc-input   [default: no-warc-input]\nDistributed computing options:\n  --distributed / --no-distributed [default: no-distributed]\n  --n-workers INTEGER              [default: 1]\n  --node INTEGER                   [default: 1]\n  --port INTEGER                   [default: 8866]\n  --help                           Show this message and exit.\n\n```\nWe will explain the distributed computing capabilities later. Input directory is allowed to have recursive subdirectories with files. It can process HTML files or WARC files. In this case, it will recompress the WARC efficiently, after stripping out all the tags. Example:\n```\ncitius@pc:~$ pyplexity tag-remover ./html_source --output-dir ./output\nComputed 1124 files in 0:00:00.543175.\n```\n## Distributed mode (cluster)\n\n## Interfacing from Python\n\n\n## Building the package\n\n```\ngit clone https://github.com/citiususc/pyplexity && cd pyplexity\ncurl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -\nsource $HOME/.poetry/env\npoetry build\npip3 install dist/pyplexity-X.X.X-py3-none-any.whl\n```\n',
    'author': 'Manuel de Prada Corral',
    'author_email': 'manuel.deprada.corral@usc.es',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)

