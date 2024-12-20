from langchain.chains import RetrievalQA
from langchain.globals import set_debug
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_community import BigQueryVectorStore, VertexFSVectorStore
from langchain_google_vertexai import VertexAI, VertexAIEmbeddings
from src.config.appconfig import env_config
# Split the documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
)
doc_splits = text_splitter.split_documents(documents)

# Add chunk number to metadata
for idx, split in enumerate(doc_splits):
    split.metadata["chunk"] = idx


from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_community import BigQueryVectorStore


embedding_model = VertexAIEmbeddings(
    model_name="textembedding-gecko@latest", project=env_config.project_id
)

bq_store = BigQueryVectorStore(
    project_id=env_config.project_id,
    dataset_name=DATASET,
    table_name=TABLE,
    location=env_config.region,
    embedding=embedding_model,
)

bq_store.add_documents(doc_splits)

from langchain_google_vertexai import VertexAI
from langchain.chains import RetrievalQA

llm = VertexAI(model_name="gemini-pro")

retriever = bq_store.as_retriever()

search_query = "How many miles can I drive the 2024 Google Starlight until I need an oil change?"

retrieval_qa = RetrievalQA.from_chain_type(
    llm=llm, chain_type="stuff", retriever=retriever
)
