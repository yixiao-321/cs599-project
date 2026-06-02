from langchain_openai import ChatOpenAI
from app.config import config

def get_deepseek_client():
    return ChatOpenAI(
        model_name=config.MODEL_NAME,
        openai_api_key=config.DEEPSEEK_API_KEY,
        openai_api_base=config.DEEPSEEK_BASE_URL,
        temperature=0.1
    )