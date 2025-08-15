from openai import OpenAI
from core.config import settings
from typing import Dict, Any, List, Optional
import asyncio
import json
import hashlib


class QwenClient:
    def __init__(self):
        """
        初始化Qwen客户端
        """
        self.client = OpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_API_BASE
        )
        self.model_name = settings.QWEN_MODEL_NAME

    def _generate_consistent_id(self, agent_name: str) -> str:
        """
        根据智能体名称生成一致的ID
        
        Args:
            agent_name: 智能体名称
            
        Returns:
            str: 一致的智能体ID
        """
        return hashlib.md5(agent_name.encode('utf-8')).hexdigest()

    def parse_intent(self, query: str) -> List[Dict[str, str]]:
        """
        解析用户意图并返回需要调用的智能体列表
        
        Args:
            query: 用户查询
            
        Returns:
            List[Dict[str, str]]: 智能体列表
        """
        # 构建提示词
        prompt = f"""
        你是一个智能体调度系统，需要根据用户的问题决定应该由哪个智能体来处理。
        请分析以下用户查询，并确定最适合处理该查询的智能体。

        用户查询: "{query}"

        可用的智能体包括:
        1. 初二数学助手 - 专门解答初二下学期数学问题的智能体，包括代数、几何等知识点

        请按照以下格式回复:
        {{
            "agents": [
                {{
                    "id": "agent-id",
                    "name": "智能体名称",
                    "description": "智能体描述"
                }}
            ]
        }}

        如果问题是数学相关的，请推荐"初二数学助手"智能体。
        如果问题不是数学相关的，请回复空的智能体列表。
        只返回JSON格式的结果，不要添加其他解释。
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一个智能体调度系统，能够根据用户问题选择合适的智能体。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            print(f"response---------{response}")
            # 解析响应
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
                agents = result.get("agents", [])
                # 为每个智能体生成一致的ID
                for agent in agents:
                    agent_name = agent.get("name", "")
                    if agent_name:
                        agent["id"] = self._generate_consistent_id(agent_name)
                print(f"agents---------{agents}")
                return agents
            else:
                return []
        except Exception as e:
            # 出错时返回空列表
            print(f"解析意图时出错: {e}")
            return []

    async def execute_math_task(self, query: str) -> Dict[str, Any]:
        """
        执行数学任务，调用Qwen模型解答数学问题
        
        Args:
            query: 数学问题查询
            
        Returns:
            Dict[str, Any]: 数学问题解答结果
        """
        # 构建数学问题解答的提示词
        prompt = f"""
        你是一个专业的初二数学老师，能够详细解答各种初二数学问题。
        请解答以下数学问题，并提供详细的解题过程：

        问题: "{query}"

        请按照以下结构回复:
        1. 问题分析: 简要分析问题类型和解题思路
        2. 解题步骤: 详细列出解题的每一步
        3. 最终答案: 给出最终的答案
        4. 相关知识点: 列出涉及的数学知识点

        请用中文回复，确保解答清晰易懂，适合初二学生理解。
        """

        try:
            # 使用asyncio运行阻塞的API调用
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "你是一个专业的初二数学老师，能够详细解答各种初二数学问题。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1500
                )
            )

            # 返回结果
            answer = response.choices[0].message.content
            if not answer:
                answer = "无法生成解答"
            
            return {
                "result": f"初二数学问题解答: {query}",
                "explanation": answer,
                "formula": "根据具体问题而定",
                "steps": ["请参考解答过程"],
                "final_answer": "请查看详细解答"
            }
        except Exception as e:
            # 出错时返回错误信息
            print(f"执行数学任务时出错: {e}")
            return {
                "result": "错误",
                "explanation": f"解答过程中出现错误: {str(e)}",
                "formula": "",
                "steps": [],
                "final_answer": "无法解答"
            }

    def execute_generic_task(self, agent_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行通用任务
        
        Args:
            agent_id: 智能体ID
            input_data: 输入数据
            
        Returns:
            Dict[str, Any]: 任务执行结果
        """
        query = input_data.get("query", "")
        
        prompt = f"""
        你是一个通用任务处理助手，需要处理各种类型的任务。
        请处理以下任务请求：

        任务ID: {agent_id}
        请求内容: "{query}"

        请提供适当的回复来处理这个任务。
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一个通用任务处理助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            result = response.choices[0].message.content
            if not result:
                result = "无法生成回复"
            
            return {
                "result": f"Processed by agent {agent_id}",
                "input": input_data,
                "output": result
            }
        except Exception as e:
            # 出错时返回错误信息
            print(f"执行通用任务时出错: {e}")
            return {
                "result": "错误",
                "input": input_data,
                "output": f"任务执行过程中出现错误: {str(e)}"
            }