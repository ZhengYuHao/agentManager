from pydantic import BaseModel
from typing import List, Optional


class Settings(BaseModel):
    PROJECT_NAME: str = "Agent Manager System"
    API_V1_STR: str = "/api/v1"
    QWEN_API_KEY: Optional[str] = None
    QWEN_MODEL_NAME: str = "qwen2.5-32b"
    QWEN_API_BASE: Optional[str] = None
    
    # 支持的智能体类型
    SUPPORTED_AGENT_TYPES: List[str] = ["scheduler", "worker"]
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()