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
        content = content.decode(errors="ignore").encode("ascii", errors="ignore")
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