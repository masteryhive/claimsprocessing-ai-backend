import re


def extract_from_settlement_offer(text:str,team_summaries:dict):
    # Extract Type of Incident
    return {
        "settlementOffer": text.replace("\n", "<br/>"),
        "discoveries": team_summaries["pre_report"]["discoveries"]
    }
