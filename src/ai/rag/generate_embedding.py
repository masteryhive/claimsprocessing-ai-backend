from langchain_google_community import BigQueryVectorStore
from langchain_google_vertexai import VertexAIEmbeddings
from src.config.appconfig import env_config

BQ_DATASET = "56gftr54"
BQ_TABLE = "policy_embeddings"

embedding_model = VertexAIEmbeddings(
    model_name="textembedding-gecko@latest", project=env_config.project_id
)
bq_store = BigQueryVectorStore(
    project_id=env_config.project_id,
    location=env_config.region,
    dataset_name=BQ_DATASET,
    table_name=BQ_TABLE,
    embedding=embedding_model,
    )
def embed_and_store_in_bigquery(documents:list)->BigQueryVectorStore:
    bq_store.add_documents(documents)
    return bq_store