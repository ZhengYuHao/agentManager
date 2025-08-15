from openai import OpenAI
from core.config import settings
from typing import Dict, Any, List, Optional
import asyncio
import json
import hashlib
import os

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

    def _get_agent_prompt(self, agent_name: str) -> str:
        """
        根据agent名称获取对应的提示词
        
        Args:
            agent_name: 智能体名称
            
        Returns:
            str: 提示词内容
        """
        # 将智能体名称映射到对应的提示词文件
        agent_prompt_mapping = {
            "初二数学助手": "math_agent_prompt.txt",
            "生物学助手": "biology_agent_prompt.txt",
            "古诗助手": "poetry_agent_prompt.txt"
        }
        
        prompt_file_name = agent_prompt_mapping.get(agent_name)
        if not prompt_file_name:
            # 如果找不到特定的提示词文件，返回默认提示词
            return """你是一个专业的{agent_name}，请根据你的专业领域回答用户问题。"""
        
        prompt_file_path = os.path.join(PROJECT_ROOT, "prompt", prompt_file_name)
        try:
            with open(prompt_file_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            # 如果找不到文件，使用默认提示词
            return """你是一个专业的{agent_name}，请根据你的专业领域回答用户问题。"""

    def parse_intent(self, query: str) -> List[Dict[str, str]]:
        """
        解析用户意图并返回需要调用的智能体列表
        
        Args:
            query: 用户查询
            
        Returns:
            List[Dict[str, str]]: 智能体列表
        """
        # 从文件读取提示词
        prompt_file_path = os.path.join(PROJECT_ROOT, "prompt", "intent_prompt.txt")
        try:
            with open(prompt_file_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()
        except FileNotFoundError:
            # 如果找不到文件，使用默认提示词
            prompt_template = """你是一个智能体调度系统，需要根据用户的问题决定应该由哪个智能体来处理。
请分析以下用户查询，并确定最适合处理该查询的智能体。

用户查询: "{query}"

可用的智能体包括:
1. 初二数学助手 - 专门解答初二下学期数学问题的智能体，包括代数、几何等知识点
2. 古诗助手 - 专门处理古诗相关问题的智能体，包括古诗赏析、创作、背诵等
3. 生物学助手 - 专门解答生物学相关问题的智能体，包括细胞生物学、遗传学、生态学等

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
如果问题是古诗相关的，请推荐"古诗助手"智能体。
如果问题是生物学相关的，请推荐"生物学助手"智能体。
如果问题不是数学、古诗或生物学相关的，请回复空的智能体列表。
只返回JSON格式的结果，不要添加其他解释。"""

        # 构建提示词
        print("999999999999999999")
        try:
            prompt = prompt_template.format(query=query)
        except Exception as e:
            print(f"格式化提示词时出错: {e}")
            print(f"prompt_template内容: {prompt_template}")
            print(f"query内容: {query}")
            # 使用默认模板
            prompt = f"""你是一个智能体调度系统，需要根据用户的问题决定应该由哪个智能体来处理。
请分析以下用户查询，并确定最适合处理该查询的智能体。

用户查询: "{query}"

可用的智能体包括:
1. 初二数学助手 - 专门解答初二下学期数学问题的智能体，包括代数、几何等知识点
2. 古诗助手 - 专门处理古诗相关问题的智能体，包括古诗赏析、创作、背诵等
3. 生物学助手 - 专门解答生物学相关问题的智能体，包括细胞生物学、遗传学、生态学等

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
如果问题是古诗相关的，请推荐"古诗助手"智能体。
如果问题是生物学相关的，请推荐"生物学助手"智能体。
如果问题不是数学、古诗或生物学相关的，请回复空的智能体列表。
只返回JSON格式的结果，不要添加其他解释。"""
        print(f"prompt---------{prompt}")
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一个智能体调度系统，能够根据用户问题选择合适的智能体，你能选择的智能体有多个。"},
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

    def get_agent_prompt(self, agent_name: str, question: str) -> str:
        """
        获取特定agent的提示词并格式化
        
        Args:
            agent_name: 智能体名称
            question: 用户问题
            
        Returns:
            str: 格式化后的提示词
        """
        prompt_template = self._get_agent_prompt(agent_name)
        try:
            return prompt_template.format(question=question, agent_name=agent_name)
        except Exception as e:
            print(f"格式化{agent_name}提示词时出错: {e}")
            print(f"prompt_template内容: {prompt_template}")
            print(f"question内容: {question}")
            # 返回一个默认的提示词
            return f"""你是一个专业的{agent_name}，请根据你的专业领域回答用户问题。
            
用户问题: "{question}"

请用清晰、易懂的语言回答。"""
        
    def _read_prompt_from_file(self, filename: str) -> str:
        """
        从文件中读取提示词
        
        Args:
            filename: 提示词文件名
            
        Returns:
            str: 提示词内容
        """
        prompt_file_path = os.path.join(PROJECT_ROOT, "prompt", filename)
        try:
            with open(prompt_file_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    async def execute_math_task(self, query: str) -> Dict[str, Any]:
        """
        执行数学任务，调用Qwen模型解答数学问题
        
        Args:
            query: 数学问题查询
            
        Returns:
            Dict[str, Any]: 数学问题解答结果
        """
        # 从文件读取系统提示词和用户提示词
        system_prompt = self._read_prompt_from_file("system_math_prompt.txt")
        if not system_prompt:
            system_prompt = "你是一个专业的初二数学老师，能够详细解答各种初二数学问题。"
            
        user_prompt_template = self._read_prompt_from_file("user_math_prompt.txt")
        if not user_prompt_template:
            user_prompt_template = """你是一个专业的初二数学老师，能够详细解答各种初二数学问题。
请解答以下数学问题，并提供详细的解题过程：

问题: "{query}"

请按照以下结构回复:
1. 问题分析: 简要分析问题类型和解题思路
2. 解题步骤: 详细列出解题的每一步
3. 最终答案: 给出最终的答案
4. 相关知识点: 列出涉及的数学知识点

请用中文回复，确保解答清晰易懂，适合初二学生理解。"""
            
        # 构建数学问题解答的提示词
        try:
            user_prompt = user_prompt_template.format(query=query)
        except Exception as e:
            print(f"格式化数学助手提示词时出错: {e}")
            print(f"user_prompt_template内容: {user_prompt_template}")
            print(f"query内容: {query}")
            # 使用默认模板
            user_prompt = f"""你是一个专业的初二数学老师，能够详细解答各种初二数学问题。
请解答以下数学问题，并提供详细的解题过程：

问题: "{query}"

请按照以下结构回复:
1. 问题分析: 简要分析问题类型和解题思路
2. 解题步骤: 详细列出解题的每一步
3. 最终答案: 给出最终的答案
4. 相关知识点: 列出涉及的数学知识点

请用中文回复，确保解答清晰易懂，适合初二学生理解。"""
            
        try:
            # 使用asyncio运行阻塞的API调用
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
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
            return {
                "result": f"处理数学问题时出错: {query}",
                "explanation": f"错误信息: {str(e)}",
                "formula": "",
                "steps": [],
                "final_answer": "处理失败"
            }

    async def execute_poetry_task(self, query: str) -> Dict[str, Any]:
        """
        执行古诗任务，调用Qwen模型处理古诗相关问题
        
        Args:
            query: 古诗相关问题查询
            
        Returns:
            Dict[str, Any]: 古诗问题解答结果
        """
        # 从文件读取系统提示词和用户提示词
        system_prompt = self._read_prompt_from_file("system_poetry_prompt.txt")
        if not system_prompt:
            system_prompt = "你是一个专业的古典文学老师，能够详细解答各种古诗相关问题。"
            
        user_prompt_template = self._read_prompt_from_file("user_poetry_prompt.txt")
        if not user_prompt_template:
            user_prompt_template = """你是一个专业的古典文学老师，能够详细解答各种古诗相关问题。
请处理以下古诗相关问题，并提供详细的解答：

问题: "{query}"

请按照以下结构回复:
1. 问题分析: 简要分析问题类型和解答思路
2. 详细解答: 详细回答问题的各个方面
3. 相关知识点: 列出涉及的古诗知识点或文学常识

请用中文回复，确保解答清晰易懂，适合古诗爱好者理解。"""
            
        # 构建古诗问题解答的提示词
        try:
            user_prompt = user_prompt_template.format(query=query)
        except Exception as e:
            print(f"格式化古诗助手提示词时出错: {e}")
            print(f"user_prompt_template内容: {user_prompt_template}")
            print(f"query内容: {query}")
            # 使用默认模板
            user_prompt = f"""你是一个专业的古典文学老师，能够详细解答各种古诗相关问题。
请处理以下古诗相关问题，并提供详细的解答：

问题: "{query}"

请按照以下结构回复:
1. 问题分析: 简要分析问题类型和解答思路
2. 详细解答: 详细回答问题的各个方面
3. 相关知识点: 列出涉及的古诗知识点或文学常识

请用中文回复，确保解答清晰易懂，适合古诗爱好者理解。"""
            
        try:
            # 使用asyncio运行阻塞的API调用
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
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
                "result": f"古诗问题解答: {query}",
                "explanation": answer,
                "author": "根据具体问题而定",
                "dynasty": "根据具体问题而定",
                "poem": "根据具体问题而定"
            }
        except Exception as e:
            return {
                "result": f"处理古诗问题时出错: {query}",
                "explanation": f"错误信息: {str(e)}",
                "author": "",
                "dynasty": "",
                "poem": ""
            }

    async def execute_biology_task(self, query: str) -> Dict[str, Any]:
        """
        执行生物学任务，调用Qwen模型解答生物学问题
        
        Args:
            query: 生物学问题查询
            
        Returns:
            Dict[str, Any]: 生物学问题解答结果
        """
        # 从文件读取系统提示词和用户提示词
        system_prompt = self._read_prompt_from_file("system_biology_prompt.txt")
        if not system_prompt:
            system_prompt = "你是一个专业的生物学老师，能够详细解答各种生物学问题。"
            
        user_prompt_template = self._read_prompt_from_file("user_biology_prompt.txt")
        if not user_prompt_template:
            user_prompt_template = """你是一个专业的生物学老师，能够详细解答各种生物学问题。
请解答以下生物学问题，并提供详细的解释：

问题: "{query}"

请按照以下结构回复:
1. 问题分析: 简要分析问题类型和解题思路
2. 详细解答: 详细解释问题的各个方面
3. 相关知识点: 列出涉及的生物学知识点

请用中文回复，确保解答清晰易懂，适合生物学学习者理解。"""
            
        # 构建生物学问题解答的提示词
        try:
            user_prompt = user_prompt_template.format(query=query)
        except Exception as e:
            print(f"格式化生物学助手提示词时出错: {e}")
            print(f"user_prompt_template内容: {user_prompt_template}")
            print(f"query内容: {query}")
            # 使用默认模板
            user_prompt = f"""你是一个专业的生物学老师，能够详细解答各种生物学问题。
请解答以下生物学问题，并提供详细的解释：

问题: "{query}"

请按照以下结构回复:
1. 问题分析: 简要分析问题类型和解题思路
2. 详细解答: 详细解释问题的各个方面
3. 相关知识点: 列出涉及的生物学知识点

请用中文回复，确保解答清晰易懂，适合生物学学习者理解。"""

        try:
            # 使用asyncio运行阻塞的API调用
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
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
                "result": f"生物学问题解答: {query}",
                "explanation": answer,
                "key_points": ["请参考详细解答"],
                "related_terms": ["根据具体问题而定"],
                "example": "根据具体问题而定"
            }
        except Exception as e:
            return {
                "result": f"处理生物学问题时出错: {query}",
                "explanation": f"错误信息: {str(e)}",
                "key_points": [],
                "related_terms": [],
                "example": ""
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
        
        # 从文件读取系统提示词和用户提示词
        system_prompt = self._read_prompt_from_file("system_generic_prompt.txt")
        if not system_prompt:
            system_prompt = "你是一个通用任务处理助手。"
            
        user_prompt_template = self._read_prompt_from_file("user_generic_prompt.txt")
        if not user_prompt_template:
            user_prompt_template = """你是一个通用任务处理助手，需要处理各种类型的任务。
请处理以下任务请求：

任务ID: {agent_id}
请求内容: "{query}"

请提供适当的回复来处理这个任务。"""
        
        # 构建通用任务的提示词
        try:
            user_prompt = user_prompt_template.format(agent_id=agent_id, query=query)
        except Exception as e:
            print(f"格式化通用任务助手提示词时出错: {e}")
            print(f"user_prompt_template内容: {user_prompt_template}")
            print(f"agent_id内容: {agent_id}, query内容: {query}")
            # 使用默认模板
            user_prompt = f"""你是一个通用任务处理助手，需要处理各种类型的任务。
请处理以下任务请求：

任务ID: {agent_id}
请求内容: "{query}"

请提供适当的回复来处理这个任务。"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
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
            return {
                "result": f"处理问题时出错: {query}",
                "answer": f"错误信息: {str(e)}"
            }