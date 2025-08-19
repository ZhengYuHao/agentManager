# -*- coding: utf-8 -*-
import hashlib
from fastapi import APIRouter
from schemas.agent import AgentCreate, AgentType
from core.agent_registry import AgentRegistry
from typing import Dict, Any
from core.utils.log_utils import info
import asyncio

biology_agent_router = APIRouter()

# 定义生物学智能体的配置
BIOLOGY_AGENT_CONFIG = {
    "name": "生物学助手",
    "description": "专门解答生物学相关问题的智能体，包括细胞生物学、遗传学、生态学等知识点",
    "agent_type": AgentType.WORKER,
    "capabilities": ["cell_biology", "genetics", "ecology", "biochemistry", "physiology"]
}

def get_biology_agent_id() -> str:
    """
    获取生物学智能体的一致性ID
    """
    return hashlib.md5(BIOLOGY_AGENT_CONFIG["name"].encode('utf-8')).hexdigest()


def create_biology_agent() -> AgentCreate:
    """
    创建生物学智能体配置对象
    """
    return AgentCreate(**BIOLOGY_AGENT_CONFIG)

def register_biology_agent(agent_registry: AgentRegistry) -> bool:
    """
    在给定的注册表中注册生物学智能体
    
    Args:
        agent_registry: 智能体注册表实例
        
    Returns:
        bool: 注册成功返回True，已存在返回False
    """
    # 检查是否已存在同名智能体
    existing_agents = agent_registry.list_agents()
    biology_agent_exists = any(agent.name == BIOLOGY_AGENT_CONFIG["name"] for agent in existing_agents)
    
    if not biology_agent_exists:
        biology_agent = create_biology_agent()
        # 使用基于名称的一致性ID注册
        agent_id = get_biology_agent_id()
        registered_agent = agent_registry.register_agent(biology_agent, agent_id)
        info(f"已自动注册默认智能体: {registered_agent.name} (ID: {registered_agent.id})")
        return True
    else:
        info("生物学助手智能体已存在，无需重复注册")
        return False

async def execute_biology_task(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行生物学任务的具体逻辑，优先使用Qwen大模型
    
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
    
    # 调用Qwen模型执行生物学任务
    result = await qwen_client.execute_biology_task(query)
    
    return result
