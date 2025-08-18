from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class AgentType(str, Enum):
    SCHEDULER = "scheduler"
    WORKER = "worker"


class AgentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OFFLINE = "offline"


class AgentBase(BaseModel):
    name: str = Field(..., description="智能体名称")
    description: str = Field(..., description="智能体描述")
    agent_type: AgentType = Field(..., description="智能体类型")
    capabilities: List[str] = Field(default=[], description="智能体能力列表")


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    capabilities: Optional[List[str]] = None
    status: Optional[AgentStatus] = None


class AgentInDB(AgentBase):
    id: str = Field(..., description="智能体唯一标识")
    status: AgentStatus = Field(default=AgentStatus.ACTIVE, description="智能体状态")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    last_heartbeat: Optional[datetime] = Field(None, description="最后心跳时间")


class AgentResponse(AgentInDB):
    pass


class Heartbeat(BaseModel):
    agent_id: str = Field(..., description="智能体ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="心跳时间")


class Message(BaseModel):
    id: str = Field(..., description="消息唯一标识")
    source_agent_id: str = Field(..., description="源智能体ID")
    target_agent_id: str = Field(..., description="目标智能体ID")
    content: Dict[str, Any] = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="消息时间戳")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="消息元数据")


class TaskRequest(BaseModel):
    query: str = Field(..., description="用户查询")
    context: Optional[Dict[str, Any]] = Field(default={}, description="上下文信息")
    session_id: Optional[str] = Field(default=None, description="会话ID")


class TaskResponse(BaseModel):
    task_id: str = Field(..., description="任务ID")
    session_id: str = Field(..., description="会话ID")
    target_agents: List[Dict[str, str]] = Field(..., description="目标智能体列表")
    response: Optional[str] = Field(None, description="响应内容")


class AgentExecutionRequest(BaseModel):
    task_id: str = Field(..., description="任务ID")
    input_data: Dict[str, Any] = Field(..., description="输入数据")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="元数据")


class AgentExecutionResponse(BaseModel):
    task_id: str = Field(..., description="任务ID")
    agent_id: str = Field(..., description="智能体ID")
    output_data: Dict[str, Any] = Field(..., description="输出数据")
    execution_time: float = Field(..., description="执行时间(秒)")
    status: str = Field(..., description="执行状态")