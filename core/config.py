from pydantic import BaseModel
from typing import List, Optional
import os
#   api_base = os.getenv("LLM_API_BASE", "http://106.227.68.83:8000/v1")
#     api_key = os.getenv("LLM_API_KEY", "dummy-key")  # Qwen API可能不需要有效的API密钥
#     model_name = os.getenv("LLM_MODEL", "qwen2.5-32b")
# id="qwen-plus",
# api_key=api_key,
# base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
class Settings(BaseModel):
    PROJECT_NAME: str = "Agent Manager System"
    API_V1_STR: str = "/api/v1"
    # QWEN_API_KEY: str = os.getenv("LLM_API_KEY", "dummy-key")  # Qwen API可能不需要有效的API密钥
    # QWEN_MODEL_NAME: str = os.getenv("LLM_MODEL", "qwen2.5-32b")
    # QWEN_API_BASE: Optional[str] = os.getenv("LLM_API_BASE", "http://106.227.68.83:8000/v1")
    QWEN_API_KEY: str = os.getenv("LLM_API_KEY", "")  # Qwen API可能不需要有效的API密钥
    QWEN_MODEL_NAME: str = os.getenv("LLM_MODEL", "qwen-plus")
    QWEN_API_BASE: Optional[str] = os.getenv("LLM_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")

    # 支持的智能体类型
    SUPPORTED_AGENT_TYPES: List[str] = ["scheduler", "worker"]
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()