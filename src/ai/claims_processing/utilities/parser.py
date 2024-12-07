from bs4 import BeautifulSoup
import re
from src.datamodels.claim_processing import CreateClaimsReport

def extract_from_claim_processing(text):
    # Extract Type of Incident
    type_match = re.search(r"Type of incident:\s*(.+)", text)
    type_of_incident = type_match.group(1).strip() if type_match else ""

    # Extract Evidence Provided
    evidence_start = text.find("Evidence Provided:")
    evidence_end = text.find("Summary of Findings:")
    evidence_content = ""
    if evidence_start != -1 and evidence_end != -1:
        evidence_text = text[evidence_start + len("Evidence Provided:"):evidence_end].strip()
        evidence_lines = re.findall(r"- (.+)", evidence_text)
        evidence_content = "<ul>\n" + "\n".join(f"<li>{line.strip()}</li>" for line in evidence_lines) + "\n</ul>"

    # Extract Summary of Findings
    findings_match = re.search(r"Summary of Findings:\s*(.+?)(?=Recommendations:)", text, re.DOTALL)
    summary_of_findings = findings_match.group(1).strip() if findings_match else ""
    
    return {
        "typeOfIncident": type_of_incident,
        "evidenceProvided": evidence_content,
        "discoveries": summary_of_findings
    }


def extract_from_policy_details(text:str,discoveries:str):
    # Extract Coverage Status
    coverage_match = re.search(r"Coverage Status:\s*(.+)", text)
    coverage_status = coverage_match.group(1).strip() if coverage_match else ""

    # Extract Details under Policy Details Summary
    details_match = re.search(r"Policy Details Summary:(.+?)\n\s+- Policy Status:", text, re.DOTALL)
    details_content = details_match.group(1).strip() if details_match else ""
    
    # Clean the details content and format as HTML list
    details_lines = re.split(r"\n", details_content)
    details_html = "<ul>\n" + "\n".join(f"<li>{line.strip()}</li>" for line in details_lines if line.strip()) + "\n</ul>"

    return {
        "coverageStatus": coverage_status,
        "policyReview": details_html,
        "discoveries": discoveries + "\n\n" +details_html
    }

def extract_claim_summary(data:str,team_summaries:dict) -> CreateClaimsReport:
    data = data.strip("xml\n").strip("```")
    fraud_score = re.search(
        r"<fraud_score>\s*(?:\/\/)?(.*?)\s*</fraud_score>", data, re.DOTALL
    )
    discoveries = re.findall(
        r"<discovery>\s*(?:\/\/)?(.*?)\s*</discovery>", data, re.DOTALL
    )
    fraud_indicators = re.findall(
        r"<indicator>\s*(?:\/\/)?(.*?)\s*</indicator>", data, re.DOTALL
    )
    claim_validation_factors = re.findall(
        r"<factor>\s*(?:\/\/)?(.*?)\s*</factor>", data, re.DOTALL
    )
    ai_recommendation = re.findall(
        r"<recommendation>\s*(?:\/\/)?(.*?)\s*</recommendation>", data, re.DOTALL
    )
    operationStatus = re.search(
        r"<claims_operation_status>\s*(?:\/\/)?(.*?)\s*</claims_operation_status>", data, re.DOTALL
    )
    try:
        fraud_score_data = fraud_score.group(1).strip() if fraud_score else 0
        if fraud_score_data == 'Information Not Available':
            fraud_score_data = 0

        team_summaries["doc"].update( {
            "fraud_score": float(fraud_score_data),
            "fraud_indicators": [indicator.strip() for indicator in fraud_indicators],
            "ai_recommendation": [
                recommendation.strip() for recommendation in ai_recommendation
            ],
            "discoveries": [discovery.strip() for discovery in discoveries],
            "operationStatus":operationStatus.group(1).strip() if operationStatus else "Information Not Available",
        })
        return team_summaries["doc"]
    except Exception as e:
        print(e)


def extract_claim_data(html_content) -> CreateClaimsReport:
    """
    Extracts data from the provided AI Claim Memo HTML template.

    Parameters:
        html_content (str): The raw HTML content of the AI Claim Memo.

    Returns:
        dict: A dictionary containing the extracted data.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract Fraud Score
    fraud_score_section = soup.find("h2", string="Fraud Check")
    fraud_score_item = (
        fraud_score_section.find_next("li") if fraud_score_section else None
    )
    fraud_score_text = fraud_score_item.text if fraud_score_item else ""
    fraud_score = (
        float(fraud_score_text.split(":")[1].split("%")[0].strip())
        if fraud_score_text
        else 0.0
    )

    # Extract Fraud Indicators
    fraud_indicators = []  # Assuming fraud indicators would need custom parsing logic

    # Extract AI Recommendation
    ai_recommendation_section = soup.find("h2", string="AI Recommendation")
    ai_recommendation_items = (
        ai_recommendation_section.find_next("ul").find_all("li")
        if ai_recommendation_section
        else []
    )
    ai_recommendation = [
        item.text.split(":")[1].strip()
        for item in ai_recommendation_items
        if ":" in item.text
    ]

    # Extract Policy Review
    policy_review_section = soup.find("h2", string="Policy Review")
    policy_review_items = (
        policy_review_section.find_next("ul").find_all("li")
        if policy_review_section
        else []
    )
    policy_review = "; ".join(
        [
            item.text.split(":")[1].strip()
            for item in policy_review_items
            if ":" in item.text
        ]
    )

    return {
        "fraud_score": fraud_score,
        "fraud_indicators": fraud_indicators,
        "ai_recommendation": ai_recommendation,
        "policy_review": policy_review,
    }
