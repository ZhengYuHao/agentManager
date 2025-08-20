# -*- coding: utf-8 -*-
"""
外部智能体处理器模块

该模块负责处理来自外部注册的智能体的任务执行逻辑
"""
import asyncio
import httpx
from typing import Dict, Any, Optional
from core.agent_registry import AgentRegistry
from schemas.agent import AgentExecutionRequest, AgentExecutionResponse
import json
from core.utils.log_utils import info, debug, error
from core.config import settings
# 外部API基础URL
EXTERNAL_API_URL = settings.EXTERNAL_API_URL


class ExternalAgentProcessor:
    """
    外部智能体处理器类
    
    负责处理外部智能体的任务执行逻辑
    """

    def __init__(self, registry: AgentRegistry):
        """
        初始化外部智能体处理器
        
        Args:
            registry: 智能体注册表实例
        """
        self.registry = registry
        self.client = httpx.AsyncClient(timeout=30.0)  # 设置30秒超时

    async def execute_agent_task(self, agent_id: str, execution_request: AgentExecutionRequest) -> AgentExecutionResponse:
        """
        执行外部智能体任务
        
        Args:
            agent_id: 智能体ID
            execution_request: 任务执行请求
            
        Returns:
            AgentExecutionResponse: 任务执行响应
            
        Raises:
            ValueError: 当智能体不存在或不是外部智能体时抛出异常
            Exception: 当任务执行失败时抛出异常
        """
        # 获取智能体信息
        agent = self.registry.get_agent(agent_id)
        if not agent:
            raise ValueError(f"未找到ID为 {agent_id} 的智能体")
        
        # 检查是否为外部智能体
        if agent.source.value != "external":
            raise ValueError(f"智能体 {agent_id} 不是外部智能体，无法使用外部处理器执行")
        
        from core.utils.log_utils import info
        info(f"开始执行外部智能体 {agent.name} 的任务")
        
        # 记录开始时间
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 根据智能体名称确定API端点并执行任务
            result = await self._execute_external_api_call(agent, execution_request)
            
            # 计算执行时间
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # 构造响应
            response = AgentExecutionResponse(
                task_id=execution_request.task_id,
                agent_id=agent_id,
                output_data=result,
                execution_time=execution_time,
                status="success"
            )
            
            info(f"外部智能体 {agent.name} 的任务执行成功，耗时: {execution_time:.2f}秒")
            return response
            
        except Exception as e:
            # 计算执行时间
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # 构造错误响应
            response = AgentExecutionResponse(
                task_id=execution_request.task_id,
                agent_id=agent_id,
                output_data={"error": str(e)},
                execution_time=execution_time,
                status="error"
            )
            
            error(f"外部智能体 {agent.name} 的任务执行失败: {e}")
            return response
        # 不在单个请求中关闭客户端，因为处理器是单例的，会在程序结束时统一关闭

    async def _execute_external_api_call(self, agent, execution_request: AgentExecutionRequest) -> Dict[str, Any]:
        """
        执行外部API调用
        
        Args:
            agent: 智能体对象
            execution_request: 任务执行请求
            
        Returns:
            Dict[str, Any]: 外部API的响应结果
        """
        # 根据智能体名称确定API端点
        api_endpoint = self._get_api_endpoint_by_agent_name(agent.name)
        
        # 构造请求数据
        request_data = {
            "user_question": self._extract_user_question(execution_request)
        }
        
        info(f"调用外部API: {api_endpoint}, 请求数据: {request_data}")
        
        try:
            # 发送POST请求到外部API
            response = await self.client.post(api_endpoint, json=request_data)
            response.raise_for_status()  # 如果状态码不是2xx会抛出异常
            
            # 解析响应数据
            response_data = response.json()
            
            # 验证响应数据格式
            if not isinstance(response_data, dict):
                raise ValueError(f"外部API返回的数据格式不正确，期望是字典，实际是 {type(response_data)}")
            
            info(f"外部API调用成功，响应数据: {response_data}")
            return response_data
            
        except httpx.RequestError as e:
            error(f"请求外部API时发生网络错误: {e}")
            raise Exception(f"网络错误: {str(e)}")
        except httpx.HTTPStatusError as e:
            error(f"外部API返回错误状态码 {e.response.status_code}: {e.response.text}")
            raise Exception(f"HTTP错误 {e.response.status_code}: {e.response.text}")
        except json.JSONDecodeError as e:
            error(f"解析外部API响应JSON时发生错误: {e}")
            raise Exception(f"JSON解析错误: {str(e)}")
        except Exception as e:
            error(f"调用外部API时发生未知错误: {e}")
            raise Exception(f"未知错误: {str(e)}")

    def _get_api_endpoint_by_agent_name(self, agent_name: str) -> str:
        """
        根据智能体名称获取API端点URL
        
        Args:
            agent_name: 智能体名称
            
        Returns:
            str: API端点URL
        """
        # 根据智能体名称映射到对应的API端点
        # 这里使用外部注册时提供的name作为key
        endpoint_mapping = {
            # 使用外部注册时的name作为key值
            "sqrt_agent": f"{EXTERNAL_API_URL}/math/sqrt",
            "parallelogram_agent": f"{EXTERNAL_API_URL}/math/parallelogram",
            "linear_function_agent": f"{EXTERNAL_API_URL}/math/linear_function",
            "data_analysis_agent": f"{EXTERNAL_API_URL}/math/data_analysis",
            "pythagorean_agent": f"{EXTERNAL_API_URL}/math/pythagorean",
            # 可以添加更多智能体名称到API端点的映射
            # 示例:
            # "生物智能体": f"{EXTERNAL_API_BASE_URL}/biology/info",
            # "诗歌助手": f"{EXTERNAL_API_BASE_URL}/poetry/generate",
        }
        
        # 记录关键日志
        debug(f"查找智能体 '{agent_name}' 的API端点")
        endpoint = endpoint_mapping.get(agent_name)
        
        if endpoint:
            debug(f"找到智能体 '{agent_name}' 的API端点: {endpoint}")
        else:
            debug(f"未找到智能体 '{agent_name}' 的API端点，使用默认端点")
            # 如果找不到映射，则使用默认端点
            endpoint = f"{EXTERNAL_API_URL}/math/sqrt"
            
        return endpoint

    def _extract_user_question(self, execution_request: AgentExecutionRequest) -> str:
        """
        从执行请求中提取用户问题
        
        Args:
            execution_request: 任务执行请求
            
        Returns:
            str: 用户问题
        """
        # 从输入数据中提取用户问题
        input_data = execution_request.input_data
        
        # 尝试从不同的可能字段中提取问题
        if isinstance(input_data, dict):
            # 尝试常见的字段名
            for field in ['query', 'question', 'content', 'text']:
                if field in input_data and isinstance(input_data[field], str):
                    return input_data[field]
        
        # 如果无法从字段中提取，则将整个输入数据转换为字符串
        return str(input_data)

    async def close(self):
        """
        关闭HTTP客户端
        """
        if self.client:
            await self.client.aclose()
            info("外部智能体处理器的HTTP客户端已关闭")


# 全局实例和便捷函数
_external_agent_processor: Optional[ExternalAgentProcessor] = None


def get_external_agent_processor(registry: AgentRegistry) -> ExternalAgentProcessor:
    """
    获取外部智能体处理器实例（单例模式）
    
    Args:
        registry: 智能体注册表实例
        
    Returns:
        ExternalAgentProcessor: 外部智能体处理器实例
    """
    global _external_agent_processor
    if _external_agent_processor is None:
        _external_agent_processor = ExternalAgentProcessor(registry)
    return _external_agent_processor


async def execute_external_agent_task(registry: AgentRegistry, agent_id: str, 
                                      execution_request: AgentExecutionRequest) -> AgentExecutionResponse:
    """
    执行外部智能体任务的便捷函数
    
    Args:
        registry: 智能体注册表实例
        agent_id: 智能体ID
        execution_request: 任务执行请求
        
    Returns:
        AgentExecutionResponse: 任务执行响应
    """
    processor = get_external_agent_processor(registry)
    try:
        response = await processor.execute_agent_task(agent_id, execution_request)
        return response
    except Exception:
        # 重新抛出异常，不关闭处理器
        raise
    # 不在每次调用后关闭处理器，因为它是单例的