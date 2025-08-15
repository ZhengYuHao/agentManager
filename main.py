from fastapi import FastAPI
from core.config import settings
import asyncio
from core.registry_manager import agent_registry

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="智能体协同管理系统，用于管理和协调不同类型智能体之间的调用",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """
    系统启动时注册路由和自动注册默认智能体
    """
    # 延迟导入并注册路由以避免循环导入
    from agents.scheduler import scheduler_router
    from agents.worker import worker_router
    from agents.manager import manager_router
    
    app.include_router(scheduler_router, prefix="/api/v1/scheduler", tags=["scheduler"])
    app.include_router(worker_router, prefix="/api/v1/worker", tags=["worker"])
    app.include_router(manager_router, prefix="/api/v1/manager", tags=["manager"])
    
    # 导入并注册数学智能体
    from agents.math_agent import register_math_agent
    register_math_agent(agent_registry)
    
    # 导入并注册古诗智能体
    from agents.poetry_agent import register_poetry_agent
    register_poetry_agent(agent_registry)
    
    # 导入并注册生物学智能体
    from agents.biology_agent import register_biology_agent
    register_biology_agent(agent_registry)

@app.get("/")
async def root():
    return {"message": "Welcome to the Agent Manager System"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)