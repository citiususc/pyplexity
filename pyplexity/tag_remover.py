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

import lxml
from lxml import etree
from lxml.html import HtmlElement, html5parser

from pyplexity.dataset_processor.dataset_processor import ContentProcessor


class HTMLTagRemover(ContentProcessor):

    def process(self, content: bytes) -> str:
        return self._remove_html_tags_lxml(content)

    def __init__(self):
        self.build_text_list = etree.XPath("//text()")

    def _remove_html_tags_lxml(self, content):
        if isinstance(content, (bytes, bytearray)):
            content = content.decode(errors="ignore")
        content = content.encode("ascii", errors="ignore")
        try:
            html: HtmlElement = lxml.html.document_fromstring(content)
        except etree.ParserError:
            return ""
        except:  # if lxml (faster parser) doesnt work, try with html5lib (slower but more stable)
            print("html5lib")
            html = html5parser.fromstring(content)
        texts = self.build_text_list(html)  # recorrido eficiente de textos con eliminacion posterior: 6.05s
        res = " ".join([s.strip() for s in texts if s.getparent().tag not in ["script", "style"]])
        return res
