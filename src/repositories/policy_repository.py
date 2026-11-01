
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
            text = page.extract_text(extraction_mode="layout") or ""

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
        stopwords = {
            "a", "as", "o", "os", "um", "uma", "uns", "umas",
            "de", "da", "das", "do", "dos", "e", "em",
            "no", "na", "nos", "nas", "para", "por",
            "com", "que", "qual", "quais", "como",
            "eu", "me", "meu", "minha", "se", "ser",
            "tem", "ter", "posso", "pode", "podem",
            "sobre", "esse", "essa", "este", "esta",
            "produto", "produtos", "loja"
        }

        words = {
            word
            for word in self.normalize(question)
            if word not in stopwords and len(word) > 2
        }

        if not words or limit <= 0:
            return []

        results = []

        for page in self.pages:
            lines = [
                line.strip()
                for line in page["text"].splitlines()
                if line.strip()
            ]

            if not lines:
                continue

            chunk_size = 8
            overlap = 2
            step = chunk_size - overlap

            for start in range(0, len(lines), step):
                chunk = " ".join(lines[start:start + chunk_size])

                chunk_words = set(self.normalize(chunk))
                score = len(words & chunk_words)

                if score > 0:
                    results.append({
                        "page": page["page"],
                        "text": chunk,
                        "score": score
                    })

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results[:limit]
