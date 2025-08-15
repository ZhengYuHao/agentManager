from fastapi import APIRouter, HTTPException, Depends
from schemas.agent import AgentCreate, AgentUpdate, AgentInDB, TaskRequest
from core.registry_manager import agent_registry
from agents.math_agent import register_math_agent
from agents.poetry_agent import register_poetry_agent
from typing import List
import time
from datetime import datetime

manager_router = APIRouter()

# 注册默认智能体的函数
def register_default_agents():
    """
    注册所有默认智能体
    """
    # 注册数学智能体
    register_math_agent(agent_registry)
    
    # 注册古诗智能体
    register_poetry_agent(agent_registry)

@manager_router.get("/agents/", response_model=List[AgentInDB])
async def list_agents():
    """
    列出所有已注册的智能体
    """
    agents = agent_registry.list_agents()
    return agents

@manager_router.post("/agents/", response_model=AgentInDB)
async def register_agent(agent_create: AgentCreate):
    """
    注册新智能体
    """
    try:
        agent = agent_registry.register_agent(agent_create)
        return agent
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@manager_router.get("/agents/{agent_id}", response_model=AgentInDB)
async def get_agent(agent_id: str):
    """
    获取指定ID的智能体信息
    """
    agent = agent_registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@manager_router.put("/agents/{agent_id}", response_model=AgentInDB)
async def update_agent(agent_id: str, agent_update: AgentUpdate):
    """
    更新智能体信息
    """
    try:
        agent = agent_registry.update_agent(agent_id, agent_update)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@manager_router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """
    删除指定的智能体
    """
    success = agent_registry.unregister_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent deleted successfully"}

@manager_router.post("/agents/{agent_id}/heartbeat")
async def heartbeat(agent_id: str):
    """
    更新智能体的心跳时间
    """
    success = agent_registry.update_heartbeat(agent_id, datetime.utcnow())
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Heartbeat updated"}