from bs4 import BeautifulSoup
import re
from src.datamodels.claim_processing import CreateClaimsReport


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
    settlement_offer = re.search(
        r"<settlement_offer>\s*(?:\/\/)?(.*?)\s*</settlement_offer>", data, re.DOTALL
    )
    operationStatus = re.search(
        r"<claims_operation_status>\s*(?:\/\/)?(.*?)\s*</claims_operation_status>", data, re.DOTALL
    )
    try:
        fraud_score_data = fraud_score.group(1).strip() if fraud_score else 0
        if fraud_score_data == 'Information Not Available':
            fraud_score_data = 0

        
        team_summaries["pre_report"].update(
            {
                "fraudScore": float(fraud_score_data),
                "fraudIndicators": [
                    indicator.strip() for indicator in fraud_indicators
                ],
                "aiRecommendation": [
                    recommendation.strip() for recommendation in ai_recommendation
                ],
                "discoveries": team_summaries["pre_report"]["discoveries"]
                + [discovery.strip() for discovery in discoveries],
                "operationStatus": (
                    operationStatus.group(1).strip()
                    if operationStatus
                    else "Information Not Available"
                ),
                "settlementOffer": (
                    settlement_offer.group(1).strip()
                    if settlement_offer
                    else "No Offer Available"
                ),
                "preLossComparison":"",
            }
        )
        return team_summaries["pre_report"]
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
