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
        print(f"valida{validated_agents}")
        # 如果仍然没有找到任何智能体，返回错误信息
        if not validated_agents:
            raise HTTPException(
                status_code=404, 
                detail="对不起，系统中没有相关智能体能处理您的问题。"
            )
        
        return TaskResponse(
            task_id=task_id,
            target_agents=validated_agents,
            response="Agents selected successfully"
        )
    except Exception as e:
        # 如果是HTTPException则重新抛出，否则包装成HTTPException
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))