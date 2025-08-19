# -*- coding: utf-8 -*-

from core.agent_registry import AgentRegistry

# 创建全局agent_registry实例
agent_registry = AgentRegistry()

# 导入外部智能体同步相关函数
from core.external_agent_sync import sync_external_agents, get_external_agent_sync

__all__ = ["agent_registry", "sync_external_agents", "get_external_agent_sync"]