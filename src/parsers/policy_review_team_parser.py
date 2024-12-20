import re

def extract_from_policy_details(text:str,discoveries:list):
    # Extract Coverage Status
    coverage_match = re.search(r"Coverage Status:\s*(.+)", text)
    coverage_status = coverage_match.group(1).strip() if coverage_match else ""

    # Extract Details under Policy Details Summary
    details_match = re.search(r"Policy Details Summary:(.+?)\n\s+- Policy Status:", text, re.DOTALL)
    details_content = details_match.group(1).strip() if details_match else ""
    # Extract Policy Status
    policy_status_match = re.search(r"(- Policy Status:\s*.+)", text)
    policy_status = policy_status_match.group(1).strip() if policy_status_match else ""

    # Clean the details content and format as HTML list
    details_lines = re.split(r"\n", details_content)
    details_html = "<ul>\n" + "\n".join(f"<li>{line.strip()}</li>" for line in details_lines if line.strip()) + "\n</ul>"

    return {
        "coverageStatus": coverage_status+"<br>"+policy_status,
        "policyReview": details_html,
        "discoveries": discoveries + ["\n\n" +details_html]
    }