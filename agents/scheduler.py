# -*- coding: utf-8 -*-

from fastapi import APIRouter, HTTPException
from schemas.agent import TaskRequest, TaskResponse
from core.llm_client import LLMClient
from core.utils.log_utils import info
import uuid
from typing import List
from core.registry_manager import agent_registry

scheduler_router = APIRouter()
llm_client = LLMClient()

# 存储对话历史的字典
conversation_history = {}

@scheduler_router.post("/process_query", response_model=TaskResponse)
async def process_user_query(task_request: TaskRequest):
    """
    处理用户查询，调度合适的智能体
    
    1. 维护对话历史
    2. 解析用户意图，确定目标智能体
    3. 验证目标智能体是否存在且处于活动状态
    4. 第一次查询强制不返回智能体，返回引导词供用户确认
    5. 后续查询按照正常逻辑推荐智能体
    6. 返回任务响应
    """
    task_id = str(uuid.uuid4())
    
    try:
        # 获取或创建会话ID
        # 如果用户没有提供session_id，则使用task_id作为临时session_id
        # 这样可以确保在单次交互中保持一致性，但无法跨多次独立请求保持会话
        info(f"session_id: {task_request.session_id}")
        session_id = task_request.session_id if task_request.session_id else task_id
        
        # 更新对话历史
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        # 添加当前查询到对话历史
        conversation_history[session_id].append({
            "role": "user",
            "content": task_request.query
        })
        
        # 检查是否是第一次查询
        is_first_query = len(conversation_history[session_id]) == 1
        # print(f"是否是第一次查询：{is_first_query},conversation_history{conversation_history}")
        # 使用最后一次用户输入作为意图识别的上下文
        last_user_input = task_request.query
        
        # 使用Qwen模型解析用户意图
        target_agents = await llm_client.parse_intent(last_user_input)
        info(f"大模型返回的agents: {target_agents}")
        
        # 打印注册表中的所有agents信息
        all_agents = agent_registry.list_agents()
        info("注册表中的所有agents:")
        for agent in all_agents:
            info(f"  ID: {agent.id}, Name: {agent.name}, Description: {agent.description}")
        
        # 验证智能体是否存在
        validated_agents = []
        for agent_info in target_agents:
            agent_id: str = agent_info.get("id", "")
            agent_name: str = agent_info.get("name", "")
            if agent_id:
                # 延迟导入避免循环导入
                agent = agent_registry.get_agent(agent_id)
                if not agent and agent_name:
                    # 如果通过ID没有找到agent，尝试通过名称查找
                    all_agents = agent_registry.list_agents()
                    for a in all_agents:
                        if a.name == agent_name:
                            agent = a
                            break
                
                if agent and agent.status.value == "active":
                    validated_agents.append({
                        "id": agent.id,
                        "name": agent.name,
                        "description": agent.description,
                        "source": agent.source.value  # 添加智能体来源信息
                    })
        info(f"验证智能体是否存在：{validated_agents}")
        # 如果是第一次查询，强制不返回智能体，而是生成引导性问题
        if is_first_query:
            # 使用LLM生成引导性问题
            guidance_prompt = f"""你是一个智能助手，需要根据用户的询问生成引导性问题。根据以下用户查询，生成合适的引导词并进行确认性询问：

用户查询: "{task_request.query}"

请分析用户可能的意图，并提供2-3个可能的选项供用户确认。按照以下格式回复：
"根据您的询问，您可能是想了解以下内容：
1. [数学相关问题]
2. [古诗相关问题] 
3. [生物相关问题]
请问您是想了解上述哪个方面的问题呢？请明确告知您的需求。"
"""
            
            try:
                from core.qwen_client import QwenClient
                qwen_client = QwenClient()
                
                guidance_response = qwen_client.client.chat.completions.create(
                    model=qwen_client.model_name,
                    messages=[
                        {"role": "system", "content": "你是一个专业的智能助手，能够根据用户问题生成引导性问题和选项。"},
                        {"role": "user", "content": guidance_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=300
                )
                
                guidance_text = guidance_response.choices[0].message.content
            except Exception as e:
                # 如果生成引导性问题失败，则使用默认提示
                guidance_text = "请告诉我您需要哪个领域的专业帮助？例如：数学、古诗或生物等"
            
            conversation_history[session_id].append({
                "role": "system",
                "content": guidance_text
            })
            
            # 第一次查询不返回任何智能体，但需要返回session_id供客户端后续使用
            return TaskResponse(
                task_id=task_id,
                session_id=session_id,  # 返回session_id供客户端后续使用
                target_agents=[],  # 第一次查询不返回任何智能体
                response=guidance_text
            )
        else:
            # 不是第一次查询，按照正常逻辑处理
            # 如果找到匹配的智能体，添加系统回复到对话历史
            if validated_agents:
                conversation_history[session_id].append({
                    "role": "system",
                    "content": "已识别到您的专业需求，正在为您匹配相关智能体"
                })
            
            # 如果没有找到明确的智能体需求，生成引导性问题
            if not validated_agents:
                # 使用LLM生成引导性问题
                guidance_prompt = f"""你是一个智能助手，需要根据用户的询问生成引导性问题。根据以下用户查询，生成合适的引导词并进行确认性询问：

用户查询: "{task_request.query}"

请分析用户可能的意图，并提供3个可能的选项供用户确认。按照以下格式回复：
"根据您的询问，您可能是想了解以下内容：
1. [数学相关问题]
2. [古诗相关问题] 
3. [生物相关问题]
请问您是想了解上述哪个方面的问题呢？请明确告知您的需求。"
"""
                
                try:
                    from core.qwen_client import QwenClient
                    qwen_client = QwenClient()
                    
                    guidance_response = qwen_client.client.chat.completions.create(
                        model=qwen_client.model_name,
                        messages=[
                            {"role": "system", "content": "你是一个专业的智能助手，能够根据用户问题生成引导性问题和选项。"},
                            {"role": "user", "content": guidance_prompt}
                        ],
                        temperature=0.3,
                        max_tokens=300
                    )
                    
                    guidance_text = guidance_response.choices[0].message.content
                except Exception as e:
                    # 如果生成引导性问题失败，则使用默认提示
                    guidance_text = "请告诉我您需要哪个领域的专业帮助？例如：数学、古诗或生物等"
                
                conversation_history[session_id].append({
                    "role": "system",
                    "content": guidance_text
                })
                
                return TaskResponse(
                    task_id=task_id,
                    session_id=session_id,  # 返回session_id供客户端后续使用
                    target_agents=[],
                    response=guidance_text
                )
            
            return TaskResponse(
                task_id=task_id,
                session_id=session_id,  # 返回session_id供客户端后续使用
                target_agents=validated_agents,
                response="已找到相关智能体"
            )
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 其他异常处理
        raise HTTPException(
            status_code=500,
            detail=f"处理查询时发生错误: {str(e)}"
        )