import re


def extract_from_settlement_offer(text: str, discoveries: dict):
    # Extract justification if present
    justification = ""
    settlement_text = text
    
    if "Justification:" in text:
        # Split text at "Justification:" and get both parts
        parts = text.split("Justification:", 1)
        settlement_text = parts[0].strip()
        justification = parts[1].strip() if len(parts) > 1 else ""

    return {
        "settlementOffer": settlement_text.replace("\n", "<br/>"),
        "discoveries": [justification]+discoveries,
    }