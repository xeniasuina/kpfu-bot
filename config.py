import os
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__)))

    GOOGLE_API_KEY: SecretStr
    GOOGLE_MODEL_NAME: SecretStr
    TG_BOT_TOKEN: SecretStr
    # DEEPSEEK_API_KEY: SecretStr
    # DEEPSEEK_MODEL_NAME: SecretStr

    DOCS_PATH:str = os.path.join(BASE_DIR, "markdown_docs")

    LM_MODEL_NAME: str = "ai-forever/FRIDA"
    CHROMA_COLLECTION_NAME: str = "test1"
    CHROMA_PATH: str = os.path.join(BASE_DIR, "chroma")
    RWKV_PATH: str = "D:\\PyCharmProjects\\rwkv\\RWKV-World-HF-Tokenizer\\scripts\\test1"
    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env")


settings = Config() # type: ignore