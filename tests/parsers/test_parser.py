import pytest
import re

# Function imports
from src.parsers.parser import extract_claim_summary
import pytest
from typing import Dict
import re

# Assuming CreateClaimsReport is a type alias or class that matches the return type
from typing import TypedDict, List

class CreateClaimsReport(TypedDict):
    fraudScore: float
    fraudIndicators: List[str]
    aiRecommendation: List[str]
    discoveries: List[str]
    operationStatus: str

def test_extract_claim_summary_complete_data():
    # Test data with all fields present
    input_data = """```xml
    <fraud_score>75.5</fraud_score>
    <discovery>Suspicious pattern identified</discovery>
    <discovery>Multiple claims in short period</discovery>
    <indicator>High claim frequency</indicator>
    <indicator>Inconsistent documentation</indicator>
    <factor>Previous claims verified</factor>
    <recommendation>Further investigation needed</recommendation>
    <claims_operation_status>In Progress</claims_operation_status>
    ```"""
    
    team_summaries = {
        "pre_report": {
            "discoveries": ["Existing discovery"],
            "fraudScore": 0,
            "fraudIndicators": [],
            "aiRecommendation": [],
            "operationStatus": ""
        }
    }
    
    result = extract_claim_summary(input_data, team_summaries)
    
    assert result["fraudScore"] == 75.5
    assert len(result["fraudIndicators"]) == 2
    assert "High claim frequency" in result["fraudIndicators"]
    assert len(result["discoveries"]) == 3  # 1 existing + 2 new
    assert "Further investigation needed" in result["aiRecommendation"]
    assert result["operationStatus"] == "In Progress"

def test_extract_claim_summary_missing_fields():
    # Test data with some fields missing
    input_data = """```xml
    <fraud_score>Information Not Available</fraud_score>
    <discovery>Single discovery</discovery>
    ```"""
    
    team_summaries = {
        "pre_report": {
            "discoveries": [],
            "fraudScore": 0,
            "fraudIndicators": [],
            "aiRecommendation": [],
            "operationStatus": ""
        }
    }
    
    result = extract_claim_summary(input_data, team_summaries)
    
    assert result["fraudScore"] == 0  # Should default to 0 for "Information Not Available"
    assert len(result["fraudIndicators"]) == 0
    assert len(result["discoveries"]) == 1
    assert len(result["aiRecommendation"]) == 0
    assert result["operationStatus"] == "Information Not Available"

def test_extract_claim_summary_with_comments():
    # Test data with XML-style comments
    input_data = """```xml
    <fraud_score>//85.0</fraud_score>
    <discovery>//Important finding</discovery>
    <indicator>//Suspicious activity</indicator>
    ```"""
    
    team_summaries = {
        "pre_report": {
            "discoveries": [],
            "fraudScore": 0,
            "fraudIndicators": [],
            "aiRecommendation": [],
            "operationStatus": ""
        }
    }
    
    result = extract_claim_summary(input_data, team_summaries)
    
    assert result["fraudScore"] == 85.0
    assert "Important finding" in result["discoveries"]
    assert "Suspicious activity" in result["fraudIndicators"]

def test_extract_claim_summary_whitespace_handling():
    # Test data with various whitespace patterns
    input_data = """```xml
    <fraud_score>
        50.0
    </fraud_score>
    <discovery>
        Finding with spaces
    </discovery>
    <indicator>
        Indicator with newlines
    </indicator>
    ```"""
    
    team_summaries = {
        "pre_report": {
            "discoveries": [],
            "fraudScore": 0,
            "fraudIndicators": [],
            "aiRecommendation": [],
            "operationStatus": ""
        }
    }
    
    result = extract_claim_summary(input_data, team_summaries)
    
    assert result["fraudScore"] == 50.0
    assert "Finding with spaces" in result["discoveries"]
    assert "Indicator with newlines" in result["fraudIndicators"]

def test_extract_claim_summary_invalid_fraud_score():
    # Test handling of invalid fraud score
    input_data = """```xml
    <fraud_score>invalid</fraud_score>
    <discovery>Valid discovery</discovery>
    ```"""
    
    team_summaries = {
        "pre_report": {
            "discoveries": [],
            "fraudScore": 0,
            "fraudIndicators": [],
            "aiRecommendation": [],
            "operationStatus": ""
        }
    }
    
    # This should raise an exception due to invalid float conversion
    with pytest.raises(Exception):
        extract_claim_summary(input_data, team_summaries)

def test_extract_claim_summary_empty_input():
    # Test handling of empty input
    input_data = "```xml\n```"
    
    team_summaries = {
        "pre_report": {
            "discoveries": ["Original discovery"],
            "fraudScore": 0,
            "fraudIndicators": [],
            "aiRecommendation": [],
            "operationStatus": ""
        }
    }
    
    result = extract_claim_summary(input_data, team_summaries)
    
    assert result["fraudScore"] == 0
    assert len(result["discoveries"]) == 1  # Should still contain original discovery
    assert result["operationStatus"] == "Information Not Available"

def test_extract_claim_summary_multiple_recommendations():
    # Test handling of multiple recommendations
    input_data = """```xml
    <fraud_score>25.0</fraud_score>
    <recommendation>Proceed with claim</recommendation>
    <recommendation>Request additional documentation</recommendation>
    ```"""
    
    team_summaries = {
        "pre_report": {
            "discoveries": [],
            "fraudScore": 0,
            "fraudIndicators": [],
            "aiRecommendation": [],
            "operationStatus": ""
        }
    }
    
    result = extract_claim_summary(input_data, team_summaries)
    
    assert len(result["aiRecommendation"]) == 2
    assert "Proceed with claim" in result["aiRecommendation"]
    assert "Request additional documentation" in result["aiRecommendation"]

# Helper function to create default team_summaries for testing
@pytest.fixture
def default_team_summaries():
    return {
        "pre_report": {
            "discoveries": [],
            "fraudScore": 0,
            "fraudIndicators": [],
            "aiRecommendation": [],
            "operationStatus": ""
        }
    }