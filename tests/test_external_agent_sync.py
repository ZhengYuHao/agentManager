import pytest
import respx
from httpx import Response
from core.agent_registry import AgentRegistry
from core.external_agent_sync import ExternalAgentSync, sync_external_agents
from schemas.agent import AgentCreate, AgentType


@pytest.mark.asyncio
async def test_fetch_external_agents_success():
    """测试成功获取外部智能体列表"""
    # 模拟外部API响应
    mock_agents = [
        {
            "name": "Test Worker",
            "description": "A test worker agent",
            "agent_type": "worker",
            "capabilities": ["test", "example"]
        }
    ]
    
    with respx.mock:
        respx.get("http://192.168.1.15:8000/api/v1/agents").mock(
            return_value=Response(200, json=mock_agents)
        )
        
        registry = AgentRegistry()
        sync_instance = ExternalAgentSync(registry)
        
        agents = await sync_instance.fetch_external_agents()
        
        assert len(agents) == 1
        assert agents[0]["name"] == "Test Worker"
        assert agents[0]["agent_type"] == "worker"


@pytest.mark.asyncio
async def test_fetch_external_agents_network_error():
    """测试网络错误情况"""
    with respx.mock:
        respx.get("http://192.168.1.15:8000/api/v1/agents").mock(
            side_effect=Exception("Network error")
        )
        
        registry = AgentRegistry()
        sync_instance = ExternalAgentSync(registry)
        
        with pytest.raises(Exception):
            await sync_instance.fetch_external_agents()


@pytest.mark.asyncio
async def test_fetch_external_agents_http_error():
    """测试HTTP错误状态码"""
    with respx.mock:
        respx.get("http://192.168.1.15:8000/api/v1/agents").mock(
            return_value=Response(500, text="Internal Server Error")
        )
        
        registry = AgentRegistry()
        sync_instance = ExternalAgentSync(registry)
        
        with pytest.raises(Exception):
            await sync_instance.fetch_external_agents()


def test_map_agent_data():
    """测试智能体数据映射"""
    registry = AgentRegistry()
    sync_instance = ExternalAgentSync(registry)
    
    agent_data = {
        "name": "Test Agent",
        "description": "A test agent",
        "agent_type": "worker",
        "capabilities": ["test", "example"]
    }
    
    agent_create = sync_instance._map_agent_data(agent_data)
    
    assert isinstance(agent_create, AgentCreate)
    assert agent_create.name == "Test Agent"
    assert agent_create.description == "A test agent"
    assert agent_create.agent_type == AgentType.WORKER
    assert agent_create.capabilities == ["test", "example"]


def test_map_agent_data_with_defaults():
    """测试使用默认值的数据映射"""
    registry = AgentRegistry()
    sync_instance = ExternalAgentSync(registry)
    
    agent_data = {
        "name": "Test Agent"
    }
    
    agent_create = sync_instance._map_agent_data(agent_data)
    
    assert isinstance(agent_create, AgentCreate)
    assert agent_create.name == "Test Agent"
    assert agent_create.description == ""
    assert agent_create.agent_type == AgentType.WORKER  # 默认值
    assert agent_create.capabilities == []      # 默认值


@pytest.mark.asyncio
async def test_sync_agents_success():
    """测试成功同步智能体"""
    mock_agents = [
        {
            "name": "Test Worker",
            "description": "A test worker agent",
            "agent_type": "worker",
            "capabilities": ["test", "example"]
        }
    ]
    
    with respx.mock:
        respx.get("http://192.168.1.15:8000/api/v1/agents").mock(
            return_value=Response(200, json=mock_agents)
        )
        
        registry = AgentRegistry()
        result = await sync_external_agents(registry)
        
        assert result["total"] == 1
        assert result["registered"] == 1
        assert result["skipped"] == 0
        assert result["errors"] == 0
        
        # 验证智能体已注册
        agents = registry.list_agents()
        assert len(agents) == 1
        assert agents[0].name == "Test Worker"


@pytest.mark.asyncio
async def test_sync_agents_skip_existing():
    """测试跳过已存在的智能体"""
    mock_agents = [
        {
            "name": "Test Worker",
            "description": "A test worker agent",
            "agent_type": "worker",
            "capabilities": ["test", "example"]
        }
    ]
    
    with respx.mock:
        respx.get("http://192.168.1.15:8000/api/v1/agents").mock(
            return_value=Response(200, json=mock_agents)
        )
        
        registry = AgentRegistry()
        # 预先注册同名智能体
        agent_create = AgentCreate(
            name="Test Worker",
            description="Existing agent",
            agent_type=AgentType.WORKER,
            capabilities=[]
        )
        registry.register_agent(agent_create)
        
        # 尝试同步，应该跳过已存在的智能体
        result = await sync_external_agents(registry)
        
        assert result["total"] == 1
        assert result["registered"] == 0
        assert result["skipped"] == 1
        assert result["errors"] == 0


@pytest.mark.asyncio
async def test_sync_agents_with_overwrite():
    """测试覆盖已存在的智能体"""
    mock_agents = [
        {
            "name": "Test Worker",
            "description": "A test worker agent",
            "agent_type": "worker",
            "capabilities": ["test", "example"]
        }
    ]
    
    with respx.mock:
        respx.get("http://192.168.1.15:8000/api/v1/agents").mock(
            return_value=Response(200, json=mock_agents)
        )
        
        registry = AgentRegistry()
        # 预先注册同名智能体
        agent_create = AgentCreate(
            name="Test Worker",
            description="Existing agent",
            agent_type=AgentType.WORKER,
            capabilities=[]
        )
        registry.register_agent(agent_create)
        
        # 尝试同步并覆盖
        result = await sync_external_agents(registry, overwrite=True)
        
        assert result["total"] == 1
        assert result["registered"] == 1
        assert result["skipped"] == 0
        assert result["errors"] == 0
        
        # 验证智能体已更新
        agents = registry.list_agents()
        assert len(agents) == 1
        assert agents[0].description == "A test worker agent"
        assert agents[0].capabilities == ["test", "example"]