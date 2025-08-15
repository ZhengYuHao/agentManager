from fastapi import FastAPI
from agents.scheduler import scheduler_router
from agents.worker import worker_router
from core.config import settings
from core.agent_registry import AgentRegistry
import asyncio

# 创建全局agent_registry实例
agent_registry = AgentRegistry()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="智能体协同管理系统，用于管理和协调不同类型智能体之间的调用",
    version="1.0.0"
)

# 注册路由
app.include_router(scheduler_router, prefix="/api/v1/scheduler", tags=["scheduler"])
app.include_router(worker_router, prefix="/api/v1/worker", tags=["worker"])

# 智能体管理路由需要在下面初始化后再注册，以避免循环导入
from agents.manager import agent_manager_router

@app.on_event("startup")
async def startup_event():
    """
    系统启动时自动注册默认智能体
    """
    # 导入并注册数学智能体
    from agents.math_agent import register_math_agent
    register_math_agent(agent_registry)

@app.get("/")
async def root():
    return {"message": "Welcome to the Agent Manager System"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 在startup事件之后注册智能体管理路由，确保注册表已初始化
app.include_router(agent_manager_router, prefix="/api/v1/manager", tags=["agent_manager"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)