import re


def extract_from_fraud_checks(text, discoveries: list):
    # Extract pre-loss comparison section
    pre_loss_match = re.search(r'PreLoss Comparison:(.*?)(?=\n\nFraud Risk Assessment:|$)', text, re.DOTALL)
    pre_loss_data = pre_loss_match.group(1).strip() if pre_loss_match else ""
    
    # Extract key sections for fraud report summary
    fraud_score = re.search(r'Fraud Threshold score: (\d+)', text)
    fraud_score = fraud_score.group(1) if fraud_score else "N/A"
    
    risk_level = re.search(r'Overall Fraud Risk Level: (\w+)', text)
    risk_level = risk_level.group(1) if risk_level else "N/A"
    
    recommendations = re.search(r'Recommendations:\n(.*?)$', text, re.DOTALL)
    recommendations = recommendations.group(1).strip() if recommendations else ""
    
    # Create fraud report summary
    fraud_report_summary = (
        f"Fraud Assessment Summary:\n"
        # f"- Fraud Score: {fraud_score}\n"
        f"- Risk Level: {risk_level}\n"
        f"- Recommendations: {recommendations}"
    )
    
    return {
        "preLossComparison": pre_loss_data,
        "discoveries": discoveries + ["\n\n" + fraud_report_summary]
    }