from bs4 import BeautifulSoup
import re
from src.datamodels.co_ai import AIClaimsReport


def extract_claim_summary(data) -> AIClaimsReport:
    fraud_score = re.search(
        r"<fraud_score>\s*(?:\/\/)?(.*?)\s*</fraud_score>", data, re.DOTALL
    )
    fraud_indicators = re.findall(
        r"<indicator>\s*(?:\/\/)?(.*?)\s*</indicator>", data, re.DOTALL
    )
    policy_review = re.search(
        r"<policy_review>\s*(?:\/\/)?(.*?)\s*</policy_review>", data, re.DOTALL
    )
    type_of_incident = re.search(
        r"<type_of_incident>\s*(?:\/\/)?(.*?)\s*</type_of_incident>", data, re.DOTALL
    )
    coverage_status = re.search(
        r"<coverage_status>\s*(?:\/\/)?(.*?)\s*</coverage_status>", data, re.DOTALL
    )
    details = re.search(r"<details>\s*(?:\/\/)?(.*?)\s*</details>", data, re.DOTALL)
    evidence_provided = re.findall(
        r"<evidence>\s*(?:\/\/)?(.*?)\s*</evidence>", data, re.DOTALL
    )
    ai_recommendation = re.findall(
        r"<recommendation>\s*(?:\/\/)?(.*?)\s*</recommendation>", data, re.DOTALL
    )

    return {
        "fraud_score": float(fraud_score.group(1).strip()) if fraud_score else 0.0,
        "fraud_indicators": [indicator.strip() for indicator in fraud_indicators],
        "policy_review": policy_review.group(1).strip() if policy_review else None,
        "ai_recommendation": [
            recommendation.strip() for recommendation in ai_recommendation
        ],
        "type_of_incident": (
            type_of_incident.group(1).strip()
            if type_of_incident
            else "Information Not Available"
        ),
        "coverage_status": (
            coverage_status.group(1).strip()
            if coverage_status
            else "Information Not Available"
        ),
        "details": details.group(1).strip() if details else "Information Not Available",
        "evidence_provided": (
            [evidence.strip() for evidence in evidence_provided]
            if evidence_provided
            else ["Information Not Available"]
        ),
    }


def extract_claim_data(html_content) -> AIClaimsReport:
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
