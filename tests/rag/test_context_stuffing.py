import pytest
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime

from src.rag.context_stuffing import (
    _get_datetime,
    generate,
    download_pdf,
    retry_generate,
    process_query
)
from vertexai.preview.generative_models import GenerationResponse, Part

@pytest.fixture
def mock_model_response():
    mock_response = MagicMock(spec=GenerationResponse)
    mock_response.text = "Test response"
    return mock_response

@pytest.fixture
def mock_pdf_document():
    return Part.from_data(data=b"test pdf content", mime_type="application/pdf")

def test_get_datetime():
    # Test if the function returns a string in the correct format
    result = _get_datetime()
    assert isinstance(result, str)
    # Verify the format by trying to parse it
    datetime.strptime(result, "%B %d %Y")

@patch('src.rag.context_stuffing.model')
def test_generate(mock_model):
    mock_model.generate_content.return_value = "Test response"
    
    result = generate(prompt=["test prompt"])
    
    assert mock_model.generate_content.called
    assert result == "Test response"

@patch('requests.get')
def test_download_pdf_success(mock_get):
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_content.return_value = [b"test content"]
    mock_get.return_value = mock_response

    with patch('builtins.open', mock_open()) as mock_file:
        result = download_pdf("test/reference")
        
    assert result == "File downloaded successfully"
    mock_file.assert_called_once()

@patch('requests.get')
def test_download_pdf_failure(mock_get):
    # Mock failed response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = download_pdf("test/reference")
    
    assert "Failed to download the file" in result
    assert "404" in result

@patch('src.rag.context_stuffing.generate')
def test_retry_generate_success(mock_generate, mock_model_response, mock_pdf_document):
    mock_generate.return_value = mock_model_response
    
    result = retry_generate(
        pdf_document=mock_pdf_document,
        prompt="test prompt",
        question="test question"
    )
    
    assert result == mock_model_response
    assert mock_generate.called

@patch('src.rag.context_stuffing.generate')
def test_retry_generate_with_retry(mock_generate, mock_model_response, mock_pdf_document):
    # First call raises exception, second call succeeds
    mock_generate.side_effect = [Exception("Test error"), mock_model_response]
    
    with patch('time.sleep'):  # Mock sleep to speed up test
        result = retry_generate(
            pdf_document=mock_pdf_document,
            prompt="test prompt",
            question="test question"
        )
    
    assert result == mock_model_response
    assert mock_generate.call_count == 2

@patch('src.rag.context_stuffing.retry_generate')
def test_process_query(mock_retry_generate, mock_model_response):
    mock_retry_generate.return_value = mock_model_response
    
    with patch('builtins.open', mock_open(read_data=b"test pdf content")):
        result = process_query(
            query="test question",
            pdf_path="test.pdf"
        )
    
    assert result == "Test response"
    assert mock_retry_generate.called


def test_process_query_with_comprehensive_info():
    # Test query
    query = (
        "Analyze this vehicle insurance policy document comprehensively and provide all critical information in a structured format. "
        "Extract and present the following details in very clear informative terms:\n\n"
        "1. Policy Basics:\n"
        " - Policy period/duration\n"
        " - Policy type and coverage category\n"
        " - Premium details (annual, paid amount, payment terms)\n"
        " - Policyholder details\n\n"
        "2. Vehicle Details:\n"
        " - Make, model, and year\n"
        " - Vehicle value/sum insured\n"
        " - Vehicle usage type (private/commercial)\n\n"
        "3. Coverage Details:\n"
        " - Main coverage types (comprehensive, third party, etc.)\n"
        " - Additional coverages/riders\n"
        " - Coverage limits and sub-limits\n"
        " - Authorized repair limits\n\n"
        "4. Key Terms and Conditions:\n"
        " - All policy conditions\n"
        " - Warranties\n"
        " - Special clauses\n"
        " - Endorsements\n\n"
        "5. Exclusions and Limitations:\n"
        " - Policy exclusions\n"
        " - Geographic limitations\n"
        " - Usage restrictions\n\n"
        "6. Claims and Notification Requirements:\n"
        " - Claims procedure\n"
        " - Notification period for valid claims\n"
        " - Required documentation for claims\n"
        " - Emergency contact numbers\n"
        " - No-claim bonus details\n"
        " - Time limits for claim submission\n"
        " - Reporting requirements for accidents/incidents\n\n"
        "7. Cancellation and Modification:\n"
        " - Cancellation terms and notice periods\n"
        " - Policy modification procedures\n"
        " - Refund conditions\n\n"
        "Important Instructions:\n"
        " - Present each piece of information on a new line using `<br/>`\n"
        " - Tag each item with a dash (-)\n"
        " - Provide complete information without summarizing\n"
        " - Include all schedules and estimated values\n"
        " - List all memoranda, conditions, and clauses individually and not as summary\n"
        " - Do not mark any information as 'MISSING'\n"
        " - Do not redact or omit any information\n"
        " - Include any other important information found in the document even if not specifically requested above"
    )
    # ... rest of the test remains the same ...
    # query = (
    #     "Provide all the crucial information in this insurance policy document, including but not limited to: "
    #     "insurance period, annual premium, liabilities, premium paid, terms, policy status, memoranda, "
    #     "coverage plan/status, policy exceptions, clauses, schedules, etc.\n"
    #     "Important Instructions for this task:\n"
    #     " - To begin, carefully look through the entire document and understand the task required.\n"
    #     " - Separate each information heading into newlines using `<br/>`\n"
    #     " - Ensure all information are tagged using `-`. (e.g. <br/> - AUTHORIZED REPAIR LIMIT: ₦100,000 <br/> - ANNUAL PREMIUM: ₦180,000)\n"
    #     " - No information should be tagged as MISSING, if you do not have such information, then do not display it.\n"
    #     " - The SCHEDULE and estimated values are crucial, this means they must be provided."
    #     " - All information should be provided in full detail without summarizing. If there are multiple items under any category "
    #     "(e.g., memoranda, conditions, clauses, exceptions), list all of them individually rather than summarizing. for example: if there are many MEMORANDA, show all relevant. do not summarize as several memoranda.\n"
    #     " - Do not include registration number. Do not redact any information.\n"
    #     " - Follow these instructions to the very last detail."
    # )
    
    pdf_path = "src/ai/rag/doc/0000980404.pdf"
    
    # Execute the function
    response = process_query(query=query, pdf_path=pdf_path)
    print(response)
    # Basic assertions to verify response structure and content
    assert isinstance(response, str)
    assert response != ""
    assert "<validation>" in response
    assert "<answer>" in response
    assert "Confidence score:" in response
    assert "<br/>" in response
    
    # Check for expected formatting
    assert response.count("<br/>") >= 1  # Should have at least one line break
    assert response.count(" - ") >= 1    # Should have at least one bullet point
    
    # Check for absence of forbidden content
    assert "MISSING" not in response.upper()
    assert "REGISTRATION NUMBER" not in response.upper()
    
    # Check for presence of validation structure
    assert "Result Derivation:" in response
    assert "Context section cited:" in response
    assert "Verification Status:" in response

