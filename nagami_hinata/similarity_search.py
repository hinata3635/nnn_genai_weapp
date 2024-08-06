from langchain.document_loaders import PyPDFLoader

from split import split_pdf

import os
from dotenv import load_dotenv
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

path = "https://blog.freelance-jp.org/wp-content/uploads/2023/03/FreelanceSurvey2023.pdf"

pages = split_pdf(path)

# .envファイルを読み込む
load_dotenv()

# APIキーの登録が必要
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
openai_api_key = os.environ.get("OPENAI_API_KEY")

# 埋め込みを作成
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

chroma_index = Chroma.from_documents(pages, embeddings)

docs = chroma_index.similarity_search("「フリーランスのリモートワークの実態」について教えて。", k=2)

for doc in docs:
    print(doc.page_content)
    print()