from bs4 import BeautifulSoup
import re
from src.models.claim_processing import CreateClaimsReport
from src.error_trace.errorlogger import system_logger

def extract_claim_summary(data:str, discoveries: list) -> CreateClaimsReport:
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
        report_discoveries = [discovery.strip() for discovery in discoveries]

        return {
               "fraudScore": float(fraud_score_data),
               "fraudIndicators": [
                    indicator.strip() for indicator in fraud_indicators
                ],
                "aiRecommendation": [
                    recommendation.strip() for recommendation in ai_recommendation
                ],
                "discoveries": discoveries + ["<br/><br/>" + "<br/>".join(report_discoveries)],
                  "operationStatus": (
                    operationStatus.group(1).strip()
                    if operationStatus
                    else "Information Not Available"
                ),
        }
    except Exception as e:
        system_logger.error(error=e)

