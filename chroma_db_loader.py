import hashlib
from pathlib import Path
import re
import time
import os
import faulthandler
import chromadb
from loguru import logger

from IPython.display import Markdown
from langchain_chroma import Chroma
from langchain.embeddings.base import Embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from typing import List

RAW_DOCS_FOLDER = 'markdown_docs'
TABLE_DOCS_FOLDER = 'many_chunks_docs'
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

class CustomEmbeddings(Embeddings):
    def __init__(self, model):
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        embedding = self.model.encode([query])[0]
        return embedding.tolist()


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
    length_function=len
)
client = chromadb.HttpClient(host="localhost", port=8000)
logger.info("chroma db client initialized")
model = SentenceTransformer("shibing624/text2vec-base-multilingual")
embeddings_model = CustomEmbeddings(model)


def compute_id(text):
    """Генерирует уникальный ID на основе хэша текста."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def normalize_prikaz(text: str) -> str:
    # Склеиваем одиночные буквы в слова (например, П Р И К А З -> ПРИКАЗ)
    text = re.sub(r'(?<=\b)([А-ЯЁ])(?:\s+([А-ЯЁ])){2,}(?=\b)', lambda m: ''.join(m.group(0).split()), text)
    # Убираем экранированные символы
    text = text.replace('\\_', '_')
    # Убираем лишние пробелы
    text = re.sub(r'\s+', ' ', text)
    # Убираем пробелы вокруг кавычек
    text = re.sub(r'«\s+', '«', text)
    text = re.sub(r'\s+»', '»', text)
    return text.strip()

def load_md_file(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        content = re.sub(r'<!-- image -->\n*', '', content)
        sections = re.split(r'(?=##)', content)
        
        data = []
        ministry_text = "МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ ФЕДЕРАЛЬНОЕ ГОСУДАРСТВЕННОЕ АВТОНОМНОЕ ОБРАЗОВАТЕЛЬНОЕ УЧРЕЖДЕНИЕ ВЫСШЕГО ОБРАЗОВАНИЯ «КАЗАНСКИЙ (ПРИВОЛЖСКИЙ) ФЕДЕРАЛЬНЫЙ УНИВЕРСИТЕТ»"
        ministry_added = False
        
        for section in sections:
            section = section.strip()
            match = re.match(r'^#+\s*(.*)', section)
            title = match.group(1).strip() if match else ""

            # Убираем заголовки
            section = re.sub(r'^#+\s*', '', section)
            section = re.sub(r'\n+', ' ', section)
            section = normalize_prikaz(section)  # Предполагается, что функция определена
            doc = Markdown(data=section)  # Предполагается, что класс Markdown определён
            text = doc.data
            
            # Проверка на текст министерства
            if ministry_text in text:
                if not ministry_added:
                    data.append({"text": text, "title": title})
                    ministry_added = True
                continue
            # Фильтрация по длине
            if len(text.strip()) > 100:
                data.append({"text": text, "title": title})
    
    return data

def split_text(text: str):
    chunks = text_splitter.split_text(text)
    return chunks

def load_files():
    file_paths = []
    file_paths.extend(list(Path(RAW_DOCS_FOLDER).rglob(f'*.md')))
    file_paths.extend(list(Path(TABLE_DOCS_FOLDER).rglob(f'*.md')))

    data = []
    seen_ids =set()
    duplicate_count = 0
    for path in file_paths:
        sections = load_md_file(path)
        for section in sections:
            text = section['text']
            title = section['title']
            file_name =path

            chunks = split_text(text)
            for index, chunk in enumerate(chunks):
                doc_id = compute_id(chunk)
                if doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    metadata = {
                        "file_name": file_name.name,
                        "section_title": title,
                        "chunk_number": index if len(chunks) > 1 else None,
                    }

                    data.append({"text": chunk, "metadata": {"id": doc_id, **metadata}})
                else:
                    duplicate_count += 1

    logger.info(f"Количество дубликатов: {duplicate_count}")

    return data


def generate_chroma_db():
    try:
        start_time = time.time()
        logger.info("Загрузка модели эмбеддингов... ")

        # embeddings = HuggingFaceEmbeddings(
        #     model_name="ai-forever/FRIDA",
        #     model_kwargs={"device": "cpu"},
        #     encode_kwargs={"normalize_embeddings": True}
        # )
        logger.info(f"Модель загружена за {time.time() - start_time:.2f} сек")

        logger.info("Создание ChromaDB")
        documents = load_files()

        start_time = time.time()
        chroma_db = Chroma.from_texts(
            texts=[item["text"] for item in documents],
            embedding=embeddings_model,
            ids=[str(item["metadata"]["id"]) for item in documents],
            metadatas=[item["metadata"] for item in documents],
            # persist_directory="./chroma",
            collection_name="documents1",
            client=client
        )
        logger.info(f"Chroma DB создана за {time.time() - start_time:.2f} сек")

        return chroma_db
    except Exception as e:
        logger.error("error: ", e)
        raise




def load_chroma_db(name: str):
    logger.info("Загрузка модели эмбеддингов...")
    # embeddings = HuggingFaceEmbeddings(
    #     model_name="ai-forever/FRIDA",
    #     model_kwargs={"device": "cpu"},
    #     encode_kwargs={"normalize_embeddings": True}
    # )
    db = Chroma(
        # persist_directory='./chroma',
        embedding_function=embeddings_model,
        collection_name=name
    )

    logger.success("Успешное подключение к ChromaDB")
    return db

def search(query: str, k: int = 4):
    try:
        chroma_db = load_chroma_db("test1")
        results = chroma_db.similarity_search_with_score(
            query, k=k
        )

        logger.info(f"Найдено {len(results)} результатов для запроса: {query}")
        formatted_results = []
        for doc, score in results:
            formatted_results.append(
                {
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": score,
                }
            )
        return formatted_results


    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    # init_chroma_db_loader()
    faulthandler.enable()
    generate_chroma_db()
    print("hello world")
    # for index in search(query="Положения об отпуске для сотрудников казанского федерального университета", k=6):
    #     print(index)

    