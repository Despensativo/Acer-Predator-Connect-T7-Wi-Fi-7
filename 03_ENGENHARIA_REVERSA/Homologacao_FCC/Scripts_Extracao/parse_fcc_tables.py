import sys
sys.stdout.reconfigure(encoding="utf-8")
from html.parser import HTMLParser

class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_td = False
        self.row = []
        self.rows = []
        self.text = ""

    def handle_starttag(self, tag, attrs):
        if tag in ("td", "th"):
            self.in_td = True
            self.text = ""

    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self.in_td = False
            self.row.append(self.text.strip())
        elif tag == "tr":
            if self.row:
                self.rows.append(self.row)
            self.row = []

    def handle_data(self, data):
        if self.in_td:
            self.text += data

with open("fcc_hlzt7.html", encoding="utf-8") as f:
    content = f.read()

parser = TableParser()
parser.feed(content)
for r in parser.rows:
    print(" | ".join(r))
