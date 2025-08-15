from fastapi import APIRouter, HTTPException
from schemas.agent import TaskRequest, TaskResponse
from core.llm_client import LLMClient
import uuid
from typing import List

scheduler_router = APIRouter()
llm_client = LLMClient()


@scheduler_router.post("/process_query", response_model=TaskResponse)
async def process_user_query(task_request: TaskRequest):
    """
    处理用户查询，调度合适的智能体
    
    1. 解析用户意图，确定目标智能体
    2. 验证目标智能体是否存在且处于活动状态
    3. 如果没有找到匹配的智能体，尝试查找数学相关智能体
    4. 返回任务响应
    """
    task_id = str(uuid.uuid4())
    
    try:
        # 使用Qwen模型解析用户意图
        target_agents = await llm_client.parse_intent(task_request.query)
        
        # 验证智能体是否存在
        validated_agents = []
        for agent_info in target_agents:
            agent_id: str = agent_info.get("id", "")
            if agent_id:
                # 延迟导入避免循环导入
                from core.registry_manager import agent_registry
                agent = agent_registry.get_agent(agent_id)
                if agent and agent.status.value == "active":
                    validated_agents.append({
                        "id": agent.id,
                        "name": agent.name,
                        "description": agent.description
                    })
        
        # 如果没有找到匹配的智能体，尝试查找数学相关智能体
        if not validated_agents:
            from core.registry_manager import agent_registry
            all_workers = agent_registry.list_agents("worker", "active")
            
            # 通过模块化方式检查数学智能体
            from agents.math_agent import MATH_AGENT_CONFIG
            math_agents = [agent for agent in all_workers 
                          if MATH_AGENT_CONFIG["name"] == agent.name]
            
            for agent in math_agents:
                validated_agents.append({
                    "id": agent.id,
                    "name": agent.name,
                    "description": agent.description
                })
        
        return TaskResponse(
            task_id=task_id,
            target_agents=validated_agents,
            response="Agents selected successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))