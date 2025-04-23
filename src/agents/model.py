import os
from google.adk.models.lite_llm import LiteLlm

MODEL_PROVIDER = "openai"
REASONING_MODEL = "doubao-1-5-thinking-pro-250415"

API_BASE = "https://ark.cn-beijing.volces.com/api/v3/"
API_KEY = os.getenv("OPENAI_API_KEY")       # your secret key


def create_reasoning_model():
    return LiteLlm(
        model=f"{MODEL_PROVIDER}/{REASONING_MODEL}",
        api_key=API_KEY,
        api_base=API_BASE,
    )
