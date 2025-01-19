def get_preloss(policy_id: str) -> str:
    """
    Generate the pre-loss image URL for a given policy ID.

    Args:
        policy_id (str): The policy ID for which to generate the pre-loss image URL.

    Returns:
        str: The URL of the pre-loss image.
    """
    base_url = "gs://masteryhive-insurance-claims/rawtest/preloss"
    modified_reference = policy_id.replace("/", "-")
    file_url = f"{base_url}/preloss_{modified_reference}.jpg"
    return file_url