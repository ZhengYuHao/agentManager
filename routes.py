from fastapi import APIRouter

def register_routes(app):
    """注册所有路由到FastAPI应用"""
    # 使用延迟导入避免循环导入
    from agents.scheduler import scheduler_router
    from agents.worker import worker_router
    from agents.manager import agent_manager_router
    
    # 注册所有子路由
    app.include_router(scheduler_router, prefix="/api/v1/scheduler", tags=["scheduler"])
    app.include_router(worker_router, prefix="/api/v1/worker", tags=["worker"])
    app.include_router(agent_manager_router, prefix="/api/v1/manager", tags=["agent_manager"])
    
# 延迟导入所有路由以避免循环导入
def get_main_router():
    from agents.scheduler import scheduler_router
    from agents.worker import worker_router
    from agents.manager import agent_manager_router
    
    # 创建主路由器并包含所有子路由
    main_router = APIRouter()
    
    # 注册所有子路由
    main_router.include_router(scheduler_router, prefix="/api/v1/scheduler", tags=["scheduler"])
    main_router.include_router(worker_router, prefix="/api/v1/worker", tags=["worker"])
    main_router.include_router(agent_manager_router, prefix="/api/v1/manager", tags=["agent_manager"])
    
    return main_router