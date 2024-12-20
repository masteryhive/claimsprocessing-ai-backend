import re


def extract_from_settlement_offer(text):
    # Extract Type of Incident
    return {
        "settlementOffer": text,
    }
