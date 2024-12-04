from google.cloud import storage
from langchain_community.document_loaders import PyPDFLoader

FOLDER_NAME = "rawtest/ZG"

def download_pdf_from_bucket(bucket_name, folder_name, file_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"{folder_name}/{file_name}")
    local_path = f"./{file_name}"
    blob.download_to_filename(local_path)
    return local_path

def load_and_chunk_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    for document in documents:
        doc_md = document.metadata
        document_name = doc_md["source"].split("/")[-1]
        # derive doc source from Document loader
        doc_source_prefix = "/".join(FOLDER_NAME.split("/")[:3])
        doc_source_suffix = "/".join(doc_md["source"].split("/")[4:-1])
        source = f"{doc_source_prefix}/{doc_source_suffix}"
        document.metadata = {"source": source, "document_name": document_name}
    return documents