from google.cloud import bigquery

# function to Get part prices from Google Cloud Big Query
def get_part_price(make: str, model: str, bodyType:str, year: int, part: str, condition:str) -> dict:
    """
    Get price details for a specific car part
    """
    client = bigquery.Client()
    dataset_id = "infrastructure-staging-418710.mh_insurance_ai"

    # Normalize "saloon" to "sedan" for consistency
    if bodyType == "saloon":
        bodyType = "sedan"

    with open('src/queries/price_query.sql', 'r') as file:
        query = file.read()

    query = query.format(dataset_id=dataset_id)

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("make", "STRING", make),
            bigquery.ScalarQueryParameter("model", "STRING", model),
            bigquery.ScalarQueryParameter("year", "INT64", year),
            bigquery.ScalarQueryParameter("part", "STRING", part),
            bigquery.ScalarQueryParameter("condition", "STRING", condition)
        ]
    )
    
    try:
        results = client.query(query, job_config=job_config).result()
        
        # Convert to dict for easier handling
        for row in results:
            return {
                "price": row.price,
                "last_updated": row.last_updated
            }
            
        return None  # Return None if no results found
        
    except Exception as e:
        print(f"Error querying price: {str(e)}")
        return None

