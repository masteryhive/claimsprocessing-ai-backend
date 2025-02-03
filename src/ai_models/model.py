from src.config.appconfig import env_config
import vertexai

# function to initiate VertexAI
def init_vertexai():
    vertexai.init(
        project=env_config.project_id,
        location=env_config.region,
        staging_bucket=env_config.staging_bucket,
    )
