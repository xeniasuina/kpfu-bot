import faulthandler
import time
from typing import Any, Dict, List, Literal
import os

import chromadb
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from loguru import logger

from config import settings
from transformers import AutoModelForCausalLM


class ChatWithAI:
    def __init__(self, provider: Literal["gemini"] = "gemini"):
        start_time = time.time()
        logger.info("Initializing Chat with AI")
        self.provider = provider
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.LM_MODEL_NAME,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        logger.info(f"Embeddings model initialized, time: {time.time() - start_time:.2f}")

        start_time = time.time()
        if provider == "gemini":
            self.llm = ChatGoogleGenerativeAI(
                api_key=settings.GOOGLE_API_KEY.get_secret_value(),
                model=settings.GOOGLE_MODEL_NAME.get_secret_value(),
                temperature=0.4
            )
        elif provider == "hgrn":
            self.llm = AutoModelForCausalLM.from_pretrained("OpenNLPLab/HGRN-1B", trust_remote_code=True)
        else:
            raise NotImplementedError
        logger.info(f"Google model initialized, time: {time.time() - start_time:.2f}")

        start_time = time.time()
        chromadb.api.client.SharedSystemClient.clear_system_cache()
        chroma_client = chromadb.HttpClient(host="localhost", port=8000)
        self.chroma_db = Chroma(
            # persist_directory=settings.CHROMA_PATH,
            embedding_function=self.embeddings,
            collection_name=settings.CHROMA_COLLECTION_NAME,
            client=chroma_client,
        )
        logger.info(f"Chroma model initialized, time: {time.time() - start_time:.2f}")

    def get_relevant_context(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        try:
            results = self.chroma_db.similarity_search(query, k=k)
            return [
                {
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                }
                for doc in results
            ]
        except Exception as e:
            logger.error(f"Failed to get relevant context: {e}")
            return []

    @staticmethod
    def format_context(context: List[Dict[str, Any]]) -> str:
        formatted_context = []
        for item in context:
            metadata_str = "\n".join(f"{k}: {v}" for k, v in item["metadata"].items())
            formatted_context.append(
                f"Текст: {item['text']}\nМетаданные:\n{metadata_str}\n"
            )

        return "\n---\n".join(formatted_context)

    def generate_response(self, query: str) -> (str, List[str]):
        try:
            start_time = time.time()
            context = self.get_relevant_context(query)
            if not context:
                return "Извините, не удалось найти подходящий контекст для формирования промпта"
            formatted_context = self.format_context(context)

            messages = [
                {
                    "role": "system",
                    "content": """Ты — внутренний менеджер Казанского Федерального Университета (КФУ). Отвечаешь по делу без лишних вступлений.

                    Правила:
                    1. Сразу переходи к сути, без фраз типа "На основе контекста"
                    2. Используй только факты. Если точных данных нет — отвечай общими фразами о Казанском Федеральном Университете, но не придумывай конкретику
                    3. Используй обычный текст без форматирования
                    4. Включай ссылки только если они есть в контексте
                    6. При упоминании файлов делай это естественно, например: "Я прикреплю инструкцию, где подробно описаны шаги"
                    7. На приветствия отвечай доброжелательно, на негатив — с легким юмором
                    8. Можешь при ответах использовать общую информацию из открытых источников по Казанскому Федеральному Университету, но опирайся на контекст
                    9. Если пользователь спрашивает о ценах, планах или технических характеристиках — давай конкретные ответы из контекста
                    10. Если пользователь спрашивает о КФУ, это значит что он спрашивает про Казанский Федеральный Университет
        
                    Персонализируй ответы, упоминая имя пользователя если оно есть в контексте. Будь краток, информативен и полезен.""",
                },
                {
                    "role": "user",
                    "content": f"Вопрос: {query}\n Контекст: {formatted_context}",
                }
            ]

            inner_response = self.llm.invoke(messages)
            logger.info(f"Response time: {time.time() - start_time:.2f}")
            if hasattr(inner_response, "content"):
                used_docs = set()
                for item in context:
                    temp_doc = item['metadata']['file_name']
                    temp_doc = temp_doc.replace('_table', '')
                    used_docs.add(temp_doc)

                formatted_docs = set()
                for doc in used_docs:
                    if 'sveden' in doc:
                        parsed_link = doc.replace('-', '/')
                        parsed_link = parsed_link.replace('.md', '')
                        new_doc = f"https://kpfu.ru/{parsed_link}"
                        formatted_docs.add(new_doc)
                        continue
                    new_filename = os.path.splitext(doc)[0] + ".pdf"
                    file_path = os.path.join("dataset", new_filename)
                    if os.path.exists(file_path):
                        formatted_docs.add(file_path)

                return str(inner_response.content), formatted_docs

            return str(inner_response).strip(), []
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return "Failed to generate response"

if __name__ == "__main__":
    faulthandler.enable()
    chat = ChatWithAI(provider="gemini")
    print("\n=== Чат с ИИ ===\n")

    while True:
        query = input("Ввод: ")
        if (query.lower() == "exit"):
            print("bb")
            break

        print("\nИИ печатает...", end="\r")
        response = chat.generate_response(query)
        print(" " * 20, end="\r")  # Очищаем "ИИ печатает..."
        print(f"ИИ: {response}\n")
