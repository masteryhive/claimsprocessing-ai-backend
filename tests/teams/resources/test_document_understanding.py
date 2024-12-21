import pytest
from unittest.mock import patch, Mock
from src.teams.resources.document_understanding import invoice_entity_extraction
from langchain_core.messages import HumanMessage, AIMessage

@pytest.fixture
def mock_pdf_processing():
    with patch('src.teams.resources.document_understanding.download_pdf') as mock_download, \
         patch('src.teams.resources.document_understanding.pdf_page_to_base64') as mock_base64:
        mock_download.return_value = "fake/path/to/pdf"
        mock_base64.return_value = "fake_base64_string"
        yield

@pytest.fixture
def mock_llm_response():
    mock_response = AIMessage(content="""
    - Invoice Information:
        - Invoice Number: INV-2024-001
        - Date: 2024-03-15
        - Vehicle: Toyota Camry (ABC-123-XY)
    - Items and Cost:
        - Front Bumper Repair: 1 x ₦50,000 = ₦50,000
        - Labour Cost: 3hrs x ₦2,000 = ₦6,000
    - Total Cost: ₦56,000
    - Invoice Narration and Purpose: Repair of front bumper damage due to minor collision
    """)
    with patch('src.teams.resources.document_understanding.llm_flash') as mock_llm:
        mock_llm.invoke.return_value = mock_response
        yield mock_response.content

def test_invoice_entity_extraction(mock_pdf_processing, mock_llm_response):
    # Arrange
    test_url = "https://example.com/test.pdf"
    
    # Act
    result = invoice_entity_extraction(test_url)
    
    # Assert
    assert isinstance(result, str)
    assert "Invoice Information" in result
    assert "Items and Cost" in result
    assert "Total Cost" in result
    assert "Invoice Narration and Purpose" in result
    assert "₦56,000" in result