import os
from haystack.nodes import (
    FileTypeClassifier,
    TextConverter,
    PDFToTextConverter,
    MarkdownConverter,
    DocxToTextConverter,
    PreProcessor,
)
from haystack.pipelines import Pipeline
from haystack.pipelines import DocumentSearchPipeline
from haystack.nodes import DensePassageRetriever, EmbeddingRetriever
from haystack.document_stores import PineconeDocumentStore
from dotenv import load_dotenv
from RealtimeSTT import AudioToTextRecorder
# Load environment variables
load_dotenv()

# Initialize converters
text_converter = TextConverter()
pdf_converter = PDFToTextConverter()
md_converter = MarkdownConverter()
docx_converter = DocxToTextConverter()
preprocessor = PreProcessor()

# Setup document store
pincone_key = os.getenv("PINECONE_KEY")
document_store = PineconeDocumentStore(
    api_key=pincone_key,
    similarity="cosine",
    environment="us-east1-gcp",
    index="knowledge",
    embedding_dim=768,
)

retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1",
)

# Initialize search pipeline
search_pipeline = DocumentSearchPipeline(retriever)

# Initialize file type classifier
file_type_classifier = FileTypeClassifier()

# Setup pipeline
indexing_pipeline = Pipeline()
indexing_pipeline.add_node(
    component=file_type_classifier, name="FileTypeClassifier", inputs=["File"]
)
indexing_pipeline.add_node(
    component=text_converter,
    name="TextConverter",
    inputs=["FileTypeClassifier.output_1"],
)
indexing_pipeline.add_node(
    component=pdf_converter, name="PdfConverter", inputs=["FileTypeClassifier.output_2"]
)
indexing_pipeline.add_node(
    component=md_converter,
    name="MarkdownConverter",
    inputs=["FileTypeClassifier.output_3"],
)
indexing_pipeline.add_node(
    component=docx_converter,
    name="DocxConverter",
    inputs=["FileTypeClassifier.output_4"],
)
indexing_pipeline.add_node(
    component=preprocessor,
    name="PreProcessor",
    inputs=["TextConverter", "PdfConverter", "MarkdownConverter", "DocxConverter"],
)
indexing_pipeline.add_node(
    component=document_store, name="DocumentStore", inputs=["PreProcessor"]
)


# Function to index files in a folder
def index_folder(folder_path="files"):
    file_paths = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            file_paths.append(file_path)
    indexing_pipeline.run(file_paths=file_paths)
    document_store.update_embeddings(retriever)


def delete_all_documents():
    document_store.delete_documents(index="knowledge")
