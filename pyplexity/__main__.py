import datetime
import os
import time
from pathlib import Path

import typer
import multiprocessing

from tqdm import tqdm

from pyplexity import distributed_files_server
from pyplexity.PerlPerplexityComputer import TrigramPerplexityComputer, BigramPerplexityComputer, \
    PerplexityProcessor
from pyplexity.dataset_processor.dataset_processor import DatasetProcessor
from pyplexity.tag_remover import HTMLTagRemover

app = typer.Typer()


@app.command()
def tag_remover(base_dir: str = '../data/warc',
                output_dir: str = '../data/warc_out',
                warc_input: bool = False,
                distributed: bool = False,
                n_workers: int = 1,
                node: int = 1,
                port: int = 8866,
                ):
    processor = DatasetProcessor(base_dir=base_dir, output_dir=output_dir, content_processor=HTMLTagRemover())
    execute_processor(base_dir, distributed, n_workers, node, port, processor, warc_input)


@app.command()
def fileserver(base_dir: str = '../../data/warc', port: int = 8866):
    distributed_files_server.main(base_dir, port)


@app.command()
def bulk_perplexity(perpl_model: str = '../../trec-pipeline-2021/nlp-improvements/perplexity/models/bigrams_cord19.st',
                    perpl_limit: float = 2000.0,
                    trigrams: bool = typer.Option(False, "--trigrams"),
                    base_dir: str = '../data/warc',
                    output_dir: str = '../data/warc_out',
                    warc_input: bool = False,
                    distributed: bool = False,
                    n_workers: int = 1,
                    node: int = 1,
                    port: int = 8866):
    if trigrams:
        perpl_computer = TrigramPerplexityComputer(perpl_model)
    else:
        perpl_computer = BigramPerplexityComputer(perpl_model)
    content_processor = PerplexityProcessor(perpl_computer, perpl_limit)
    processor = DatasetProcessor(base_dir=base_dir, output_dir=output_dir, content_processor=content_processor)
    execute_processor(base_dir, distributed, n_workers, node, port, processor, warc_input)


@app.command()
def perplexity(text: str,
               perpl_model: str = '../../trec-pipeline-2021/nlp-improvements/perplexity/models/bigrams_cord19.st',
               trigrams: bool = typer.Option(False, "--trigrams")):
    if trigrams:
        perpl_computer = TrigramPerplexityComputer(perpl_model)
    else:
        perpl_computer = BigramPerplexityComputer(perpl_model)
    typer.echo(perpl_computer.compute_sentence(text))


def execute_processor(base_dir, distributed, n_workers, node, port, processor, warc_input):
    if not distributed:
        extension = ".warc.gz" if warc_input else ""
        files = [i for i in Path(base_dir).glob('**/*' + extension) if i.is_file()]
        start = time.time()
        for i, file in tqdm(enumerate(files), total=len(files)):
            processor.process_single_file(os.path.relpath(file, base_dir), i, 1, warc_input)
        print(f"Computed {len(files)} files in {str(datetime.timedelta(seconds=time.time() - start))}.")
    else:
        jobs = []
        print(f"Master thread from node{node}, PID {os.getpid()}")
        for i in range(n_workers):
            j = multiprocessing.Process(target=processor.batch_process_from_server, args=(i + 1, port))
            jobs.append(j)
        for j in jobs:
            j.start()
        for j in jobs:
            j.join()
        print(f"Node {node} finished processing all the files.")


if __name__ == "__main__":
    app()
