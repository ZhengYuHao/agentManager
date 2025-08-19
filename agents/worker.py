from fastapi import APIRouter, HTTPException
from schemas.agent import AgentExecutionRequest, AgentExecutionResponse
from core.llm_client import LLMClient
import time

worker_router = APIRouter()
llm_client = LLMClient()


@worker_router.post("/execute/{agent_id}", response_model=AgentExecutionResponse)
async def execute_agent_task(agent_id: str, execution_request: AgentExecutionRequest):
    """
    执行指定智能体的任务
    """
    # 检查智能体是否存在且活跃
    from core.registry_manager import agent_registry
    agent = agent_registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if agent.status.value != "active":
        raise HTTPException(status_code=400, detail="Agent is not active")
    
    start_time = time.time()
    
    try:
        # 检查是否为外部智能体，如果是则使用外部处理器
        if agent.source.value == "external":
            # 导入外部智能体处理器
            from agents.external_agent_processor import execute_external_agent_task
            response = await execute_external_agent_task(agent_registry, agent_id, execution_request)
            return response
        else:
            # 执行内部智能体任务，这里调用LLM客户端处理
            output_data = await llm_client.execute_task(agent_id, execution_request.input_data)
            
            execution_time = time.time() - start_time
            
            return AgentExecutionResponse(
                task_id=execution_request.task_id,
                agent_id=agent_id,
                output_data=output_data,
                execution_time=execution_time,
                status="success"
            )
    except Exception as e:
        execution_time = time.time() - start_time
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")