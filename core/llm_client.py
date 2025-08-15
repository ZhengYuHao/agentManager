from core.config import settings
from typing import List, Dict, Any
import asyncio


class LLMClient:
    def __init__(self):
        # 初始化Qwen客户端
        self.model_name = settings.QWEN_MODEL_NAME
        self.api_key = settings.QWEN_API_KEY
        self.api_base = settings.QWEN_API_BASE

    async def parse_intent(self, query: str) -> List[Dict[str, str]]:
        """
        解析用户意图并返回需要调用的智能体列表
        这里应该实际调用Qwen API，但暂时返回模拟数据
        """
        # 模拟API调用延迟
        await asyncio.sleep(0.1)
        
        # 检查查询是否与数学相关
        from agents.math_agent import MATH_AGENT_CONFIG
        math_keywords = ["数学", "几何", "代数", "方程", "函数", "三角形", "平行四边形", "因式分解", 
                        "分式", "根式", "一次函数", "反比例函数", "勾股定理", "平行四边形", "矩形", 
                        "菱形", "正方形", "梯形", "数据分析", "平均数", "中位数", "众数", "不等式",
                        "二次根式", "勾股定理", "四边形", "平移", "旋转", "中心对称"]
        
        is_math_related = any(keyword in query for keyword in math_keywords)
        
        # 如果与数学相关，返回数学智能体
        if is_math_related:
            # 查找数学智能体的实际ID
            try:
                from main import agent_registry
                math_agents = [agent for agent in agent_registry.list_agents() 
                              if MATH_AGENT_CONFIG["name"] == agent.name and agent.status.value == "active"]
                
                if math_agents:
                    # 返回实际的数学智能体
                    return [
                        {
                            "id": math_agents[0].id,
                            "name": math_agents[0].name,
                            "description": math_agents[0].description
                        }
                    ]
            except:
                # 如果无法访问agent_registry，使用默认值
                pass
            
            # 默认返回
            return [
                {
                    "id": "math-agent",
                    "name": MATH_AGENT_CONFIG["name"],
                    "description": MATH_AGENT_CONFIG["description"]
                }
            ]
        
        # 这里应该根据实际查询内容决定返回哪些智能体
        # 目前返回模拟数据
        return [
            {
                "id": "worker-1",
                "name": "DataProcessor",
                "description": "处理数据分析任务"
            },
            {
                "id": "worker-2", 
                "name": "TextGenerator",
                "description": "生成文本内容"
            }
        ]

    async def execute_task(self, agent_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行具体任务
        这里应该实际调用Qwen API，但暂时返回模拟数据
        """
        # 模拟API调用延迟
        await asyncio.sleep(0.2)
        
        # 检查是否是数学智能体
        try:
            from main import agent_registry
            agent = agent_registry.get_agent(agent_id)
            
            from agents.math_agent import MATH_AGENT_CONFIG
            if agent and MATH_AGENT_CONFIG["name"] == agent.name:
                # 模拟数学问题解答
                query = input_data.get("query", "")
                return {
                    "result": f"初二数学问题解答: {query}",
                    "explanation": "这是针对您的初二数学问题的详细解答过程...",
                    "formula": "相关数学公式展示",
                    "steps": ["步骤1", "步骤2", "步骤3"],
                    "final_answer": "最终答案"
                }
        except:
            # 如果无法访问agent_registry，继续执行默认逻辑
            pass
        
        # 根据agent_id和input_data模拟不同的处理结果
        return {
            "result": f"Processed by agent {agent_id}",
            "input": input_data,
            "output": f"Output for task from agent {agent_id}"
        }