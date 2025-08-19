# -*- coding: utf-8 -*-
import hashlib
from fastapi import APIRouter
from schemas.agent import AgentCreate, AgentType
from core.agent_registry import AgentRegistry
from typing import Dict, Any
from core.utils.log_utils import info
import asyncio

poetry_agent_router = APIRouter()



# 定义古诗智能体的配置
POETRY_AGENT_CONFIG = {
    "name": "古诗助手",
    "description": "专门处理古诗相关问题的智能体，包括古诗赏析、创作、背诵等",
    "agent_type": AgentType.WORKER,
    "capabilities": ["poetry_appreciation", "poetry_creation", "poetry_analysis", "poetry_tutoring"]
}

def get_poetry_agent_id() -> str:
    """
    获取古诗智能体的一致性ID
    """
    return hashlib.md5(POETRY_AGENT_CONFIG["name"].encode('utf-8')).hexdigest()


def create_poetry_agent() -> AgentCreate:
    """
    创建古诗智能体配置对象
    """
    return AgentCreate(**POETRY_AGENT_CONFIG)

def register_poetry_agent(agent_registry: AgentRegistry) -> bool:
    """
    在给定的注册表中注册古诗智能体
    
    Args:
        agent_registry: 智能体注册表实例
        
    Returns:
        bool: 注册成功返回True，已存在返回False
    """
    # 检查是否已存在同名智能体
    existing_agents = agent_registry.list_agents()
    poetry_agent_exists = any(agent.name == POETRY_AGENT_CONFIG["name"] for agent in existing_agents)
    
    if not poetry_agent_exists:
        poetry_agent = create_poetry_agent()
        # 使用基于名称的一致性ID注册
        agent_id = get_poetry_agent_id()
        registered_agent = agent_registry.register_agent(poetry_agent, agent_id)
        info(f"已自动注册默认智能体: {registered_agent.name} (ID: {registered_agent.id})")
        return True
    else:
        info("古诗助手智能体已存在，无需重复注册")
        return False

async def execute_poetry_task(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行古诗任务的具体逻辑，优先使用Qwen大模型
    
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
    
    # 创建并执行异步任务
    task = asyncio.create_task(qwen_client.execute_poetry_task(query))
    
    # 等待任务完成并获取结果
    result = await task
    
    return result
