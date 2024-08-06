import os
from dotenv import load_dotenv

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.indexes import VectorstoreIndexCreator
from langchain.document_loaders import TextLoader

# .envファイルを読み込む
load_dotenv()

# APIキーの登録が必要
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
openai_api_key = os.environ.get("OPENAI_API_KEY")

loader = TextLoader('./sample.txt')

text_splitter = CharacterTextSplitter(
    separator = "\n",
    chunk_size = 100,
    chunk_overlap = 0,
    length_function = len,
)

index = VectorstoreIndexCreator(
    vectorstore_cls=Chroma, # Default
    embedding=OpenAIEmbeddings(), # Default
    text_splitter=text_splitter,
).from_loaders([loader])

query = "「フリーランスのリモートワークの実態」について教えて。"
print(f"\n\n{query}")
answer = index.query(query)
print(answer)