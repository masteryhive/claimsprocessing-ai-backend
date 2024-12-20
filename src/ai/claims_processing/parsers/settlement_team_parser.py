import re


def extract_from_settlement(text):
    # Extract Type of Incident
    type_match = re.search(r"Type of incident:\s*(.+)", text)
    type_of_incident = type_match.group(1).strip() if type_match else ""

    # Extract Evidence Provided
    evidence_start = text.find("Evidence Provided:")
    evidence_end = text.find("Summary of Findings:")
    evidence_content = []
    if evidence_start != -1 and evidence_end != -1:
        evidence_text = text[evidence_start + len("Evidence Provided:"):evidence_end].strip()
        evidence_lines = re.findall(r"- (.+)", evidence_text)
        #evidence_content = "<ul>\n" + "\n".join(f"<li>{line.strip()}</li>" for line in evidence_lines) + "\n</ul>"
        evidence_content = [line.strip() for line in evidence_lines]

    # Extract Summary of Findings
    findings_match = re.search(r"Summary of Findings:\s*(.+?)(?=Recommendations:)", text, re.DOTALL)
    summary_of_findings = findings_match.group(1).strip() if findings_match else ""
    
    return {
        "preLossComparison": type_of_incident,
        "settlementOffer": evidence_content,
    }
