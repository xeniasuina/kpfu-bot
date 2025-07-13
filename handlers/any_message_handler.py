import logging
import os
from aiogram import Router
from aiogram.types import Message, FSInputFile

from chroma_chat.chat_with_ai import ChatWithAI

any_message_router = Router()
chat = ChatWithAI(provider="gemini")
logger = logging.getLogger(__name__)

@any_message_router.message()
async def parse_message(message: Message):
    user_text = message.text.lower()
    logger.info(f"chat: {message.chat.full_name}, user_text: {user_text}")
    try:
        answer, sources = chat.generate_response(user_text)
        used_links = set()
        used_files = []
        for src in sources:
            if 'https' in src:
                used_links.add(src)
                continue

            pdf_file = FSInputFile(path=src, filename=os.path.basename(src))
            used_files.append(pdf_file)

        logger.info(f"chat: {message.chat.full_name}, answer: {answer}")
        links_text = "\n".join(used_links)
        answer += f"\n\nИсточники: \n{links_text}"
        await message.answer(answer)

        for file in used_files:
            await message.answer_document(file)

    except Exception as e:
        await message.answer("Произошла ошибка при обработке вопроса!")
        print(f"error: {e}")
