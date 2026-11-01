
import pytest
from reportlab.pdfgen import canvas

from src.repositories.policy_repository import PolicyRepository


@pytest.fixture
def policy_repository(tmp_path):
    pdf_path = tmp_path / "politicas_da_loja.pdf"

    pdf = canvas.Canvas(str(pdf_path))

    pdf.drawString(
        50,
        750,
        "Politica de Trocas e Devolucoes"
    )
    pdf.drawString(
        50,
        730,
        "O prazo para devolucao e de 7 dias corridos."
    )
    pdf.drawString(
        50,
        710,
        "O frete de devolucao e por conta da loja."
    )

    pdf.showPage()

    pdf.drawString(
        50,
        750,
        "Politica de Entregas"
    )
    pdf.drawString(
        50,
        730,
        "O prazo de entrega e de 3 dias uteis."
    )

    pdf.save()

    return PolicyRepository(data_dir=tmp_path)


def test_policy_repository_loads_pdf(policy_repository):
    assert len(policy_repository.pages) == 2


def test_policy_repository_normalizes_accents(policy_repository):
    result = policy_repository.normalize(
        "Devolução e REEMBOLSO"
    )

    assert result == [
        "devolucao",
        "e",
        "reembolso"
    ]


def test_policy_repository_finds_return_policy(policy_repository):
    results = policy_repository.search(
        "Qual é o prazo para devolução?"
    )

    assert results
    assert any(
        "7 dias corridos" in result["text"]
        for result in results
    )


def test_policy_repository_returns_page_number(policy_repository):
    results = policy_repository.search(
        "Qual é o prazo para entrega?"
    )

    assert results
    assert any(
        result["page"] == 2
        for result in results
    )


def test_policy_repository_returns_empty_for_blank_question(
    policy_repository
):
    results = policy_repository.search("   ")

    assert results == []


def test_policy_repository_respects_result_limit(policy_repository):
    results = policy_repository.search(
        "devolução",
        limit=1
    )

    assert len(results) <= 1
