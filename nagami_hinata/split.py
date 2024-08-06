from langchain.document_loaders import PyPDFLoader

def split_pdf(path: str) -> list:
    loader = PyPDFLoader(path)
    pages = loader.load_and_split()

    return pages

# for page in pages[:5]:
#     print(page.metadata['page'])
#     print(page.metadata['source'])
#     print('--------------------------------------------------')
#     print(page.page_content)
#     print('==================================================')