from core.config import settings
from typing import List, Dict, Any
import asyncio


class LLMClient:
    def __init__(self):
        # 初始化Qwen客户端
        self.model_name = settings.QWEN_MODEL_NAME
        self.api_key = settings.QWEN_API_KEY
        self.api_base = settings.QWEN_API_BASE

    async def parse_intent(self, query: str) -> List[Dict[str, str]]:
        """
        解析用户意图并返回需要调用的智能体列表
        """
        # 使用新的Qwen客户端
        from core.qwen_client import QwenClient
        qwen_client = QwenClient()
        
        # 调用Qwen客户端解析意图
        agents = qwen_client.parse_intent(query)
        return agents

    async def execute_task(self, agent_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行具体任务
        """
        # 检查是否是数学智能体
        try:
            from core.registry_manager import agent_registry
            agent = agent_registry.get_agent(agent_id)
            
            from agents.math_agent import MATH_AGENT_CONFIG, execute_math_task
            if agent and MATH_AGENT_CONFIG["name"] == agent.name:
                # 调用数学智能体的专用处理函数，该函数会使用Qwen大模型
                return await execute_math_task(input_data)
        except:
            # 如果无法访问agent_registry，继续执行默认逻辑
            pass
            
        # 检查是否是古诗智能体
        try:
            from core.registry_manager import agent_registry
            agent = agent_registry.get_agent(agent_id)
            
            from agents.poetry_agent import POETRY_AGENT_CONFIG, execute_poetry_task
            if agent and POETRY_AGENT_CONFIG["name"] == agent.name:
                # 调用古诗智能体的专用处理函数，该函数会使用Qwen大模型
                return await execute_poetry_task(input_data)
        except:
            # 如果无法访问agent_registry，继续执行默认逻辑
            pass
        
        # 对于其他智能体，使用通用的Qwen客户端
        from core.qwen_client import QwenClient
        qwen_client = QwenClient()
        return qwen_client.execute_generic_task(agent_id, input_data)