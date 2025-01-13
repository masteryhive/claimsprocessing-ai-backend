def get_preloss(policy_id:str):
    base_url = "https://storage.googleapis.com/masteryhive-insurance-claims/rawtest/preloss"
    modified_reference = policy_id.replace("/", "-")
    file_url = f"{base_url}/preloss_{modified_reference}.jpg"
    return file_url