import hashlib
from fastapi import APIRouter
from schemas.agent import AgentCreate, AgentType
from core.agent_registry import AgentRegistry
from typing import Dict, Any
import asyncio

math_agent_router = APIRouter()

# 定义数学智能体的配置
MATH_AGENT_CONFIG = {
    "name": "初二数学助手",
    "description": "专门解答初二下学期数学问题的智能体，包括代数、几何等知识点",
    "agent_type": AgentType.WORKER,
    "capabilities": ["algebra", "geometry", "problem_solving", "math_tutoring"]
}

def get_math_agent_id() -> str:
    """
    获取数学智能体的一致性ID
    """
    return hashlib.md5(MATH_AGENT_CONFIG["name"].encode('utf-8')).hexdigest()


def create_math_agent() -> AgentCreate:
    """
    创建数学智能体配置对象
    """
    return AgentCreate(**MATH_AGENT_CONFIG)

def register_math_agent(agent_registry: AgentRegistry) -> bool:
    """
    在给定的注册表中注册数学智能体
    
    Args:
        agent_registry: 智能体注册表实例
        
    Returns:
        bool: 注册成功返回True，已存在返回False
    """
    # 检查是否已存在同名智能体
    existing_agents = agent_registry.list_agents()
    math_agent_exists = any(agent.name == MATH_AGENT_CONFIG["name"] for agent in existing_agents)
    
    if not math_agent_exists:
        math_agent = create_math_agent()
        # 使用基于名称的一致性ID注册
        agent_id = get_math_agent_id()
        registered_agent = agent_registry.register_agent(math_agent, agent_id)
        print(f"已自动注册默认智能体: {registered_agent.name} (ID: {registered_agent.id})")
        return True
    else:
        print("初二数学助手智能体已存在，无需重复注册")
        return False

async def execute_math_task(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行数学任务的具体逻辑，优先使用Qwen大模型
    
    Args:
        input_data: 输入数据，包含查询和其他相关信息
        
    Returns:
        Dict[str, Any]: 处理结果
    """
    # 导入Qwen客户端
    from core.qwen_client import QwenClient
    
    # 获取查询内容
    query = input_data.get("query", "")
    
    # 创建Qwen客户端实例
    qwen_client = QwenClient()
    
    # 调用Qwen模型执行数学任务
    result = await qwen_client.execute_math_task(query)
    
    return result