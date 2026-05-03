from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def pdf_loader(path):
    pdf = PyPDFLoader(path)
    docs = pdf.load()

    text = ""
    for page in docs:
        text += page.page_content

    metadata = {
        "source": path,
        "page_count": len(docs)
    }

    return text, metadata


def split_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    return splitter.split_text(text)
