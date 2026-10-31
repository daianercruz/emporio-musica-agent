
from pathlib import Path
import re
import unicodedata

from pypdf import PdfReader


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


class PolicyRepository:

    def __init__(self, data_dir=DATA_DIR):
        pdf_path = Path(data_dir) / "politicas_da_loja.pdf"
        reader = PdfReader(pdf_path)

        self.pages = []

        for number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            if text.strip():
                self.pages.append({
                    "page": number,
                    "text": text.strip()
                })

    def normalize(self, text):
        text = unicodedata.normalize("NFKD", text.lower())
        text = "".join(
            char for char in text
            if not unicodedata.combining(char)
        )

        return re.findall(r"\w+", text)

    def search(self, question, limit=3):
        words = set(self.normalize(question))

        if not words:
            return []

        results = []

        for page in self.pages:
            paragraphs = re.split(r"\n\s*\n", page["text"])

            for paragraph in paragraphs:
                paragraph_words = set(self.normalize(paragraph))
                score = len(words & paragraph_words)

                if score > 0:
                    results.append({
                        "page": page["page"],
                        "text": paragraph.strip(),
                        "score": score
                    })

        results.sort(key=lambda item: item["score"], reverse=True)

        return results[:limit]
