
import pytest
from reportlab.pdfgen import canvas

from src.repositories.policy_repository import PolicyRepository


@pytest.fixture
def repository(tmp_path):
    pdf_path = tmp_path / "politicas_da_loja.pdf"

    pdf = canvas.Canvas(str(pdf_path))

    pdf.drawString(50, 750, "Horario de funcionamento")
    pdf.drawString(50, 730, "A loja abre aos sabados das 9h as 13h.")
    pdf.showPage()

    pdf.drawString(50, 750, "Trocas e devolucoes")
    pdf.drawString(50, 730, "Compras online podem ser devolvidas em 7 dias.")
    pdf.save()

    return PolicyRepository(tmp_path)


def test_load_pdf(repository):
    assert len(repository.pages) == 2


def test_search_opening_hours(repository):
    results = repository.search("horario sabados")

    assert results
    assert results[0]["page"] == 1


def test_search_returns_source_text(repository):
    results = repository.search("devolvidas")

    assert results
    assert "7 dias" in results[0]["text"]


def test_empty_question(repository):
    assert repository.search("") == []


def test_unknown_subject(repository):
    assert repository.search("xilofonemisterioso") == []
