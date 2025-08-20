# -*- coding: utf-8 -*-
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from core.agent_registry import AgentRegistry
from schemas.agent import AgentCreate, AgentType, AgentSource
from core.utils.log_utils import info, error, warning


# 设置日志
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

# 外部API地址
EXTERNAL_API_URL = "http://192.168.1.15:8000/api/v1/agents"


class ExternalAgentSync:
    """
    外部智能体同步类
    
    负责从外部API获取智能体信息并注册到本地注册表中
    """

    def __init__(self, registry: AgentRegistry):
        """
        初始化外部智能体同步器
        
        Args:
            registry: 智能体注册表实例
        """
        self.registry = registry
        self.client = httpx.AsyncClient(timeout=30.0)  # 设置30秒超时

    async def fetch_external_agents(self) -> List[Dict[str, Any]]:
        """
        从外部API获取智能体列表
        
        Returns:
            List[Dict[str, Any]]: 智能体信息列表
            
        Raises:
            httpx.RequestError: 当请求失败时抛出异常
            httpx.HTTPStatusError: 当HTTP状态码不是2xx时抛出异常
            ValueError: 当返回的数据格式不正确时抛出异常
        """
        try:
            info(f"正在从 {EXTERNAL_API_URL} 获取外部智能体信息")
            response = await self.client.get(EXTERNAL_API_URL)
            response.raise_for_status()  # 如果状态码不是2xx会抛出异常
            
            # 解析JSON响应
            agents_data = response.json()
            
            # 确保返回的是列表格式
            if not isinstance(agents_data, list):
                error(f"外部API返回的数据格式不正确，期望是列表，实际是 {type(agents_data)}: {agents_data}")
                # 尝试处理可能的包装格式，例如 {"agents": [...]} 或 {"data": [...]}
                if isinstance(agents_data, dict):
                    # 尝试常见的包装字段
                    for key in ['agents', 'data', 'items', 'results']:
                        if key in agents_data and isinstance(agents_data[key], list):
                            agents_data = agents_data[key]
                            info(f"从字段 '{key}' 中提取智能体列表")
                            break
                    else:
                        # 如果没有找到合适的字段，将其包装成列表
                        agents_data = [agents_data]
                        info("将单个对象包装成列表")
                
                # 如果仍然不是列表，抛出异常
                if not isinstance(agents_data, list):
                    raise ValueError(f"无法将数据转换为列表格式: {type(agents_data)}")
            
            info(f"成功获取到 {len(agents_data)} 个外部智能体")
            return agents_data
        except httpx.RequestError as e:
            error(f"请求外部API时发生网络错误: {e}")
            raise
        except httpx.HTTPStatusError as e:
            error(f"外部API返回错误状态码 {e.response.status_code}: {e.response.text}")
            raise
        except ValueError as e:
            error(f"外部API返回数据格式错误: {e}")
            raise
        except Exception as e:
            error(f"解析外部API响应时发生错误: {e}")
            raise

    def _map_agent_data(self, agent_data: Dict[str, Any]) -> AgentCreate:
        """
        将外部智能体数据映射为本地AgentCreate对象
        
        Args:
            agent_data: 外部智能体原始数据
            
        Returns:
            AgentCreate: 本地智能体创建对象
            
        Raises:
            ValueError: 当输入数据格式不正确时抛出异常
        """
        # 验证输入数据类型
        info(f"验证输入类型{agent_data}")
        if not isinstance(agent_data, dict):
            raise ValueError(f"期望agent_data为字典类型，但实际类型为: {type(agent_data)}")
        
        # 提取必要字段
        name = agent_data.get("name", "")
        description = agent_data.get("description", "")
        agent_type_str = agent_data.get("agent_type", "worker")  # 默认为worker类型
        
        # 将字符串类型的agent_type转换为AgentType枚举
        try:
            agent_type = AgentType(agent_type_str.lower())
        except ValueError:
            warning(f"未知的智能体类型: {agent_type_str}, 使用默认值worker")
            agent_type = AgentType.WORKER
            
        capabilities = agent_data.get("capabilities", [])
        
        # 创建本地AgentCreate对象，标识为外部来源
        agent_create = AgentCreate(
            name=name,
            description=description,
            agent_type=agent_type,
            capabilities=capabilities,
            source=AgentSource.EXTERNAL  # 标识为外部来源
        )
        
        return agent_create

    async def sync_agents(self, overwrite: bool = False) -> Dict[str, Any]:
        """
        同步外部智能体到本地注册表
        
        Args:
            overwrite: 是否覆盖已存在的智能体，默认为False
            
        Returns:
            Dict[str, Any]: 同步结果统计信息
        """
        stats = {
            "total": 0,
            "registered": 0,
            "skipped": 0,
            "errors": 0,
            "error_details": []
        }
        
        try:
            # 从外部API获取智能体列表
            agents_data = await self.fetch_external_agents()
            stats["total"] = len(agents_data)
            info(f"DDDDDD{agents_data}")
            # 验证数据格式
            if not isinstance(agents_data, list):
                raise ValueError(f"期望agents_data为列表类型，但实际类型为: {type(agents_data)}")
    
            # 处理每个智能体
            for i, agent_data in enumerate(agents_data):
                try:
                    # 映射数据格式
                    agent_create = self._map_agent_data(agent_data)
                    
                    # 检查智能体是否已存在
                    # 根据名称生成一致的ID
                    agent_id = self.registry._generate_consistent_id(agent_create.name)
                    agent_exists = agent_id in self.registry.agents
                    
                    # 根据overwrite参数决定是否覆盖已存在的智能体
                    if agent_exists and not overwrite:
                        info(f"智能体 {agent_create.name} 已存在，跳过注册")
                        stats["skipped"] += 1
                        continue
                    
                    # 注册智能体
                    self.registry.register_agent(agent_create, agent_id)
                    info(f"成功注册外部智能体: {agent_create.name}")
                    stats["registered"] += 1
                    
                except Exception as e:
                    agent_name = "unknown"
                    if isinstance(agent_data, dict) and "name" in agent_data:
                        agent_name = agent_data["name"]
                    elif isinstance(agent_data, dict):
                        agent_name = f"unnamed_agent_{i}"
                    else:
                        agent_name = f"invalid_data_{i}"
                        
                    error(f"注册智能体 {agent_name} 时发生错误: {e}")
                    stats["errors"] += 1
                    stats["error_details"].append({
                        "agent_name": agent_name,
                        "error": str(e)
                    })
                    
        except Exception as e:
            error(f"同步外部智能体时发生错误: {e}")
            raise
            
        finally:
            # 确保关闭HTTP客户端
            await self.client.aclose()
            
        info(f"外部智能体同步完成: {stats}")
        return stats

    async def close(self):
        """
        关闭HTTP客户端连接
        """
        await self.client.aclose()


# 全局实例和便捷函数
_external_agent_sync: Optional[ExternalAgentSync] = None


def get_external_agent_sync(registry: AgentRegistry) -> ExternalAgentSync:
    """
    获取外部智能体同步器实例（单例模式）
    
    Args:
        registry: 智能体注册表实例
        
    Returns:
        ExternalAgentSync: 外部智能体同步器实例
    """
    global _external_agent_sync
    if _external_agent_sync is None:
        _external_agent_sync = ExternalAgentSync(registry)
    return _external_agent_sync


async def sync_external_agents(registry: AgentRegistry, overwrite: bool = False) -> Dict[str, Any]:
    """
    同步外部智能体的便捷函数
    
    Args:
        registry: 智能体注册表实例
        overwrite: 是否覆盖已存在的智能体，默认为False
        
    Returns:
        Dict[str, Any]: 同步结果统计信息
    """
    sync_instance = get_external_agent_sync(registry)
    try:
        result = await sync_instance.sync_agents(overwrite)
        return result
    finally:
        await sync_instance.close()