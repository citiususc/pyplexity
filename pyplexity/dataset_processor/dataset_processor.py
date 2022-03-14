import datetime
import io
import shutil
import time
import traceback
from pathlib import Path

import nltk as nltk
import requests
from memory_tempfile import MemoryTempfile
from warcio.archiveiterator import ArchiveIterator
from warcio.bufferedreaders import DecompressingBufferedReader

from pyplexity.dataset_processor.CustomWARCWriter import CustomWARCWriter


class ContentProcessor:
    def process(self, content: bytes) -> str:
        raise NotImplementedError


class DatasetProcessor:
    def __init__(self, base_dir, output_dir, content_processor: ContentProcessor):
        nltk.download('punkt', quiet=True)
        self.base_dir = Path(base_dir)
        self.output_dir = Path(output_dir)
        self.content_processor = content_processor

    def batch_process_from_server(self, process_number, port):
        print(f"P{process_number} computing warc files...")
        file = requests.get(f"http://master:{port}/files").text  # get filenames to process from master node REST API
        i = 0
        start = time.time()
        while file != "END":
            self.process_single_file(file, i, process_number, True)
            file = requests.get(f"http://master:{port}/files").text  # ask for a new WARC file to process
            i += 1
        print(f"P{process_number} computed {i} warc files in {str(datetime.timedelta(seconds=time.time() - start))}.")

    def process_single_file(self, file, i, process_number, warc_file):
        in_file = self.base_dir / file
        out_file = self.output_dir / file
        out_file.parent.mkdir(parents=True, exist_ok=True)
        if i % 100 == 0:  # log some of the files
            print(f"P{process_number}: processing {i + 1}th file " + in_file.name)
        if warc_file:
            self.process_warc_file(in_file, out_file, i, process_number)
        else:
            with open(in_file, 'rb') as in_file, open(out_file, 'w') as out_file:
                sanitized_input = in_file.read().decode(errors="ignore").encode("ascii", errors="ignore")
                processed_text = self.content_processor.process(sanitized_input)
                out_file.write(processed_text)

    def process_warc_file(self, in_file, out_file, i, process_number):
        memfile_generator = MemoryTempfile()  # mem tempfiles generator so its faster than disk files
        with open(in_file, 'rb') as in_file, \
                memfile_generator.TemporaryFile() as temp, \
                memfile_generator.TemporaryFile() as out_buffer, \
                open(out_file, 'wb') as out_file:
            decomp = DecompressingBufferedReader(in_file, read_all_members=True)
            shutil.copyfileobj(decomp, temp)  # decompress WARC to memory tempfile
            temp.seek(0)  # restart file pointer of decompressed initial WARC after decompression
            writer = CustomWARCWriter(out_buffer, gzip=True)  # new WARC file after processing, write to memory
            for record in ArchiveIterator(temp):  # read decompressed WARC
                if record.rec_type == 'response' and record.payload_length > 0:
                    content = record.raw_stream.read()  # get webpage content from WARC
                    try:
                        new_content = self.content_processor.process(content)
                    except Exception as e:
                        print(
                            f"Exception at node {process_number} while processing record={record.rec_headers.get_header('WARC-Target-URI')} of file {in_file}: {str(e)}")
                        traceback.print_exc()
                        new_content = ""
                    # write processed text to WARC record object
                    record.raw_stream = io.BytesIO(new_content.encode('utf-8', errors='ignore'))
                    record.payload_length = record.raw_stream.getbuffer().nbytes  # update lenght of WARC record
                writer.write_record(record)  # write modified WARC record to output in-memory WARC file
            out_buffer.seek(0)  # reset output warc file pointer
            shutil.copyfileobj(out_buffer, out_file)  # copy in-memory WARC file with all new records to disk
