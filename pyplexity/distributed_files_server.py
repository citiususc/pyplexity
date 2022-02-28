import os
from pathlib import Path

import typer
from flask import Flask, request
from tqdm import tqdm

api = Flask(__name__)
file_list = []
n_files = 0
done = 0
pbar: tqdm

def new_done():
    return n_files-len(file_list)-done #hechos nuevos - done

@api.route('/files', methods=['GET'])
def get_files():
    global done
    try:
        # print(f'{(1.0 - len(file_list) / n_files) * 100.0:.2f}%')
        pbar.update(n_files-len(file_list)-done)  # hechos nuevos - done
        done = n_files-len(file_list)
        return file_list.pop()
    except IndexError:
        return "END"


@api.route('/kill', methods=['GET'])
def kill():
    shutdown_hook = request.environ.get('werkzeug.server.shutdown')
    pbar.close()
    if shutdown_hook is not None:
        shutdown_hook()
    return "Bye"


def main(base_dir: str = '../../data/warc', port: int = 8866):
    global file_list, n_files, pbar
    file_list = [str(os.path.relpath(f, base_dir)) for f in list(Path(base_dir).glob('**/*.warc.gz'))]
    file_list.reverse()
    n_files = len(file_list)
    pbar = tqdm(total=n_files)
    print(f"Starting serving files of {base_dir}")
    api.run(host="master", port=port, threaded=False)


if __name__ == "__main__":
    typer.run(main)
