from schemas.agent import AgentCreate, AgentUpdate, AgentInDB, AgentStatus
from typing import List, Dict, Optional
import uuid
from datetime import datetime
import hashlib


class AgentRegistry:
    def __init__(self):
        self.agents: Dict[str, AgentInDB] = {}

    def _generate_consistent_id(self, agent_name: str) -> str:
        """
        根据智能体名称生成一致的ID
        
        Args:
            agent_name: 智能体名称
            
        Returns:
            str: 一致的智能体ID
        """
        # 使用MD5哈希确保相同名称总是生成相同的ID
        return hashlib.md5(agent_name.encode('utf-8')).hexdigest()

    def register_agent(self, agent_create: AgentCreate, agent_id: Optional[str] = None) -> AgentInDB:
        """
        注册新智能体
        
        Args:
            agent_create: 智能体创建信息
            agent_id: 可选的预定义智能体ID，如果不提供则自动生成
        """
        if agent_id is None:
            # 检查是否可以基于名称生成一致的ID
            consistent_id = self._generate_consistent_id(agent_create.name)
            if consistent_id not in self.agents:
                agent_id = consistent_id
            else:
                # 如果基于名称的ID已存在，生成随机ID
                agent_id = str(uuid.uuid4())
        elif agent_id in self.agents:
            # 如果提供的ID已存在，抛出异常
            raise ValueError(f"Agent with ID {agent_id} already exists")
        
        agent_in_db = AgentInDB(
            id=agent_id,
            **agent_create.model_dump()
        )
        self.agents[agent_id] = agent_in_db
        return agent_in_db

    def get_agent(self, agent_id: str) -> Optional[AgentInDB]:
        """
        获取指定智能体
        """
        return self.agents.get(agent_id)

    def list_agents(self, agent_type: Optional[str] = None, status: Optional[str] = None) -> List[AgentInDB]:
        """
        获取智能体列表，支持按类型和状态过滤
        """
        agents = list(self.agents.values())
        if agent_type:
            agents = [agent for agent in agents if agent.agent_type.value == agent_type]
        if status:
            agents = [agent for agent in agents if agent.status.value == status]
        return agents

    def update_agent(self, agent_id: str, agent_update: AgentUpdate) -> Optional[AgentInDB]:
        """
        更新智能体信息
        """
        if agent_id not in self.agents:
            return None
        
        agent = self.agents[agent_id]
        update_data = agent_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        return agent

    def unregister_agent(self, agent_id: str) -> bool:
        """
        注销智能体
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False

    def update_heartbeat(self, agent_id: str, timestamp: datetime) -> bool:
        """
        更新智能体心跳时间
        """
        if agent_id in self.agents:
            self.agents[agent_id].last_heartbeat = timestamp
            return True
        return False

    def get_available_workers(self) -> List[AgentInDB]:
        """
        获取所有可用的工作智能体
        """
        return [
            agent for agent in self.agents.values()
            if agent.agent_type == "worker" and agent.status == AgentStatus.ACTIVE
        ]