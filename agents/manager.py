from fastapi import APIRouter, HTTPException
from schemas.agent import AgentCreate, AgentUpdate, AgentResponse, Heartbeat
from typing import List, Optional
from core.agent_registry import AgentRegistry

agent_manager_router = APIRouter()
agent_registry = AgentRegistry()


@agent_manager_router.post("/agents/", response_model=AgentResponse)
async def register_agent(agent: AgentCreate):
    """
    注册新智能体
    """
    try:
        agent_in_db = agent_registry.register_agent(agent)
        return agent_in_db
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@agent_manager_router.get("/agents/", response_model=List[AgentResponse])
async def list_agents(agent_type: Optional[str] = None, status: Optional[str] = None):
    """
    获取智能体列表
    """
    return agent_registry.list_agents(agent_type, status)


@agent_manager_router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """
    获取指定智能体信息
    """
    agent = agent_registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@agent_manager_router.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, agent_update: AgentUpdate):
    """
    更新智能体信息
    """
    try:
        agent = agent_registry.update_agent(agent_id, agent_update)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@agent_manager_router.delete("/agents/{agent_id}")
async def unregister_agent(agent_id: str):
    """
    注销智能体
    """
    success = agent_registry.unregister_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent unregistered successfully"}


@agent_manager_router.post("/agents/{agent_id}/heartbeat")
async def heartbeat(agent_id: str, heartbeat: Heartbeat):
    """
    智能体心跳
    """
    success = agent_registry.update_heartbeat(agent_id, heartbeat.timestamp)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Heartbeat received"}