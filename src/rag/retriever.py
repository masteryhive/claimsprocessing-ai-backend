from langchain_google_community import BigQueryVectorStore
from langchain_google_community.vertex_rank import VertexAIRank
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableSerializable
from typing import Any
from langchain_core.messages import BaseMessage
from src.config.appconfig import env_config
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from src.ai_models.llm import llm

# Retrieves relevant documents from BigQuery and refines them using a reranker.
def retrieve_from_bigquery(bq_store: BigQueryVectorStore)-> RunnableSerializable[Any, BaseMessage]:
    # Instantiate the VertexAIReranker with the SDK manager
    reranker = VertexAIRank(
        project_id=env_config.project_id,
        location_id=env_config.region,
        ranking_config="default_ranking_config",
        title_field="source",
        top_n=3,
    )
    
    basic_retriever = bq_store.as_retriever(search_kwargs={"k": 5})  # fetch top 5 documents

    # Create the ContextualCompressionRetriever with the VertexAIRanker as a Reranker
    retriever_with_reranker = ContextualCompressionRetriever(
        base_compressor=reranker, base_retriever=basic_retriever
    )
    template = """
    <context>
    {context}
    </context>

    Question:
    {query}

    Don't give information outside the context or repeat your findings.
    Answer:
    """
    prompt = PromptTemplate.from_template(template)

    reranker_setup_and_retrieval = RunnableParallel(
        {"context": retriever_with_reranker, "query": RunnablePassthrough()}
    )

    chain = reranker_setup_and_retrieval | prompt | llm
    return chain