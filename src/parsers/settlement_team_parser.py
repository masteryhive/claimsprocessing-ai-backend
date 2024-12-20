import re


def extract_from_settlement_offer(text:str):
    # Extract Type of Incident
    return {
        "settlementOffer": text.replace("\n", "<br/>"),
    }
