# PyPlexity
# Copyright (C) 2022 Manuel Prada Corral
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import math
import re
import signal
from typing import Union

import nltk
import pandas
from cached_path import cached_path
from storable import retrieve

from pyplexity.dataset_processor.dataset_processor import ContentProcessor


class PerplexityProcessor(ContentProcessor):
    def __init__(self, perpl_model, perpl_limit):
        self.perpl_model = perpl_model
        self.perpl_limit = perpl_limit
        self.threshold = 60

    def split_sentences_by_size(self, sentences: list) -> list:
        processed_list = []
        temp_text = None

        for text in sentences:
            #print(text)
            if temp_text:
                text = temp_text + text
                temp_text = None
            if len(text) >= self.threshold:
                processed_list.append(text)
            else:
                temp_text = text
        if temp_text:
            processed_list.append(temp_text)
        return processed_list

    def process(self, content: Union[str, bytes]) -> str:
        if not isinstance(content, str):
            content = content.decode(errors="ignore")
        new_content = ""
        signal.alarm(60 * 5)  # 5mins timeout
        it = nltk.sent_tokenize(content)  # timeout-limited code
        # it = self.split_sentences_by_size(sentences=content.split("."))
        #print(it)
        signal.alarm(0)  # cancel timeout
        for sent in it:
            perpl_score = self.perpl_model.compute_sentence(sent)
            # print(f"{sent} {perpl_score}")
            if perpl_score < self.perpl_limit:
                new_content += " " + sent
            else:
                new_content += f"<ppl {perpl_score}>{sent}</ppl>."
        return new_content


class PerplexityModel:
    def compute_sentence(self, sentence: str) -> float:
        pass

    def _custom_tokenize(self, x):
        x = x.translate(
            str.maketrans("ABCDEFGHIJKLMNÑOPQRSTUVWXYZ", "abcdefghijklmnÑopqrstuvwxyz")
        )
        x = x.translate(
            str.maketrans(
                "\301\311\315\323\332\307\303\325\302\312\324\300\310",
                "\341\351\355\363\372\347\343\365\342\352\364\340\350",
            )
        )
        x = re.sub(r",", " ,", x)
        x = re.sub(r";", " ;", x)
        x = re.sub(r":", " :", x)
        x = re.sub(r"\. [\w]*", " . ", x)
        x = re.sub(r"\.$", " .", x)
        x = re.sub(r"\(", " ( ", x)
        x = re.sub(r"\)", " ) ", x)
        x = re.sub(r"\"[ ]*", '" ', x)
        x = re.sub(r"[ ]*\"", ' "', x)
        x = re.sub(r"\<", " < ", x)
        x = re.sub(r"\>", " > ", x)
        x = re.sub(r"\=", " = ", x)
        x = re.sub(r"\'", " ' ", x)
        x = re.sub(r"\`", " ` ", x)
        x = re.sub(r"\?", " ? ", x)
        x = re.sub(r"\¿", " ¿ ", x)
        x = re.sub(r"\!", " ! ", x)
        x = re.sub(r"\¡", " ¡ ", x)
        x = re.sub(r"\s+", " ", x).strip()
        return x.split(" ")

    @staticmethod
    def from_str(perpl_model: str):
        try:
            data = retrieve(perpl_model)
        except FileNotFoundError:
            file = cached_path(
                "https://gitlab.citius.usc.es/pyplexity/pyplexity.pages.citius.usc.es/-/raw/master/"
                + perpl_model.replace("-", "_")
                + ".st"
            )
            print("Loading model... ", end="", flush=True)
            data = retrieve(file)
        if len(data) > 2:
            return TrigramPerplexityModel(data)
        else:
            return BigramPerplexityModel(data)


class BigramPerplexityModel(PerplexityModel):
    def __init__(self, data):
        self.bigrams: dict = data[0]
        self.unigrams: dict = data[1]
        print("Done.")

    def compute_sentence(self, sentence: str):
        tok_sentence = self._custom_tokenize(sentence)
        # tok_sentence = sentence.split()
        bigrams = zip(["#"] + tok_sentence[:-1], tok_sentence)
        log_prob_sum = 0
        for word1, word2 in bigrams:
            bigram = (word1 + " " + word2).encode("UTF-8", errors="replace")
            word1 = word1.encode("UTF-8", errors="replace")
            bi_dec = self.bigrams[bigram] if bigram in self.bigrams else 0
            uni_dec = self.unigrams[word1] if word1 in self.unigrams else 0
            log_prob_sum += math.log2((bi_dec * 0.8) + (uni_dec * 0.2) + (1 / 1000000))
        perplexity = 2 ** (-(log_prob_sum / len(tok_sentence)))
        return perplexity


class TrigramPerplexityModel(PerplexityModel):
    def __init__(self, data):
        self.trigrams: dict = data[0]
        self.bigrams: dict = data[1]
        self.unigrams: dict = data[2]
        print("Done.")

    def compute_sentence(self, sentence: str):
        tok_sentence = self._custom_tokenize(sentence)
        # tok_sentence = sentence.split()
        trigrams = zip(["#"] + tok_sentence[:-2], tok_sentence[:-1], tok_sentence)
        log_prob_sum = 0
        for word1, word2, word3 in trigrams:
            trigram = (word1 + " " + word2 + " " + word3).encode(
                "UTF-8", errors="replace"
            )
            bigram = (word1 + " " + word2).encode("UTF-8", errors="replace")
            word1 = word1.encode("UTF-8", errors="replace")
            tri_dec = self.trigrams[trigram] if trigram in self.trigrams else 0
            bi_dec = self.bigrams[bigram] if bigram in self.bigrams else 0
            uni_dec = self.unigrams[word1] if word1 in self.unigrams else 0
            log_prob_sum += math.log2(
                (tri_dec * 0.6) + (bi_dec * 0.3) + (uni_dec * 0.1) + (1 / 1000000)
            )
        perplexity = 2 ** (-(log_prob_sum / len(tok_sentence)))
        return perplexity


if __name__ == "__main__":
    bigrams_model_path = (
        "../trec-pipeline-2021/nlp-improvements/perplexity/models/bigrams_cord19.st"
    )
    computer = BigramPerplexityModel(bigrams_model_path)
    input = pandas.read_csv("raw_sentences.txt", sep=",", names=["id", "text"])
    for _, row in input.iterrows():
        new_ppl = computer.compute_sentence(row.text)
