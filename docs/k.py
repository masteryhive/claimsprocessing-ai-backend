import re

# Function to extract data
def extract_claim_summary(data):
    fraud_score = re.search(r"<fraud_score>\s*(?:\/\/)?(.*?)\s*</fraud_score>", data, re.DOTALL)
    fraud_indicators = re.findall(r"<indicator>\s*(?:\/\/)?(.*?)\s*</indicator>", data, re.DOTALL)
    policy_review = re.search(r"<policy_review>\s*(?:\/\/)?(.*?)\s*</policy_review>", data, re.DOTALL)
    ai_recommendation = re.findall(r"<recommendation>\s*(?:\/\/)?(.*?)\s*</recommendation>", data, re.DOTALL)

    return {
        "fraud_score": float(fraud_score.group(1).strip()) if fraud_score else 0.0,
        "fraud_indicators": [indicator.strip() for indicator in fraud_indicators],
        "policy_review": policy_review.group(1).strip() if policy_review else None,
        "ai_recommendation": [recommendation.strip() for recommendation  in ai_recommendation],
    }

# Sample Input Data
data = """
<claim_summary>
  <fraud_score>
  85
  </fraud_score>
  <fraud_indicators>
  <indicator>
  // Suspicious claim amount
  </indicator>
  <indicator>
  // Policyholder flagged for previous fraud
  </indicator>
  </fraud_indicators>
  <policy_review>
  // Policy is consistent but needs further investigation
  </policy_review>
  <claims_action_recommendation>
  <recommendation>
  // Refer to claims investigator for detailed review
  </recommendation>
  <recommendation>
    // Refer to claims investigator for detailed review
  </recommendation>
  </claims_action_recommendation>
</claim_summary>
"""

# Extract data
extracted_data = extract_claim_summary(data)

# Output result
print(extracted_data)
