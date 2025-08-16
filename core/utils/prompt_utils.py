#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词工具模块
用于处理提示词文件的读取、管理和格式化等功能
"""

import os
import json
from typing import Dict, Any, Optional
from core.config import settings

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PromptManager:
    """提示词管理器"""
    
    def __init__(self):
        """初始化提示词管理器"""
        self.prompt_dir = os.path.join(PROJECT_ROOT, "prompt")
    
    def read_prompt_from_file(self, filename: str) -> str:
        """
        从文件中读取提示词
        
        Args:
            filename: 提示词文件名
            
        Returns:
            str: 提示词内容
        """
        prompt_file_path = os.path.join(self.prompt_dir, filename)
        try:
            with open(prompt_file_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    def get_agent_prompt(self, agent_name: str) -> str:
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
        
        return self.read_prompt_from_file(prompt_file_name)
    
    def format_prompt(self, template: str, **kwargs) -> str:
        """
        格式化提示词模板
        
        Args:
            template: 提示词模板
            **kwargs: 格式化参数
            
        Returns:
            str: 格式化后的提示词
        """
        try:
            return template.format(**kwargs)
        except Exception as e:
            print(f"格式化提示词时出错: {e}")
            print(f"template内容: {template}")
            print(f"参数内容: {kwargs}")
            raise


# 全局实例
prompt_manager = PromptManager()


def read_prompt_from_file(filename: str) -> str:
    """
    从文件中读取提示词的工具函数
    
    Args:
        filename: 提示词文件名
        
    Returns:
        str: 提示词内容
    """
    return prompt_manager.read_prompt_from_file(filename)


def get_agent_prompt(agent_name: str) -> str:
    """
    根据agent名称获取对应的提示词
    
    Args:
        agent_name: 智能体名称
        
    Returns:
        str: 提示词内容
    """
    return prompt_manager.get_agent_prompt(agent_name)


def format_prompt(template: str, **kwargs) -> str:
    """
    格式化提示词模板的工具函数
    
    Args:
        template: 提示词模板
        **kwargs: 格式化参数
        
    Returns:
        str: 格式化后的提示词
    """
    return prompt_manager.format_prompt(template, **kwargs)