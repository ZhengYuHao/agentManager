# -*- coding: utf-8 -*-
import logging

import os
from datetime import datetime
from typing import Optional

# 创建logs目录（如果不存在）
LOGS_DIR = "logs"
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)


class LogManager:
    """日志管理器，提供统一的日志记录功能"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, log_level: int = logging.INFO):
        if LogManager._initialized:
            return
            
        self.logger = logging.getLogger("agent_manager")
        self.logger.setLevel(log_level)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 创建文件处理器
            log_filename = f"agent_manager_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(
                os.path.join(LOGS_DIR, log_filename), 
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            
            # 创建格式器，包含模块名和行号
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加处理器到日志记录器
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
        
        LogManager._initialized = True
    
    def debug(self, message: str):
        """记录调试信息"""
        self.logger.debug(message, stacklevel=3)  # 跳过debug->_log->实际调用者
    
    def info(self, message: str):
        """记录一般信息"""
        self.logger.info(message, stacklevel=3)
    
    def warning(self, message: str):
        """记录警告信息"""
        self.logger.warning(message, stacklevel=3)
    
    def error(self, message: str):
        """记录错误信息"""
        self.logger.error(message, stacklevel=3)
    
    def critical(self, message: str):
        """记录严重错误信息"""
        self.logger.critical(message, stacklevel=3)


# 创建全局日志管理器实例
log_manager = LogManager()


def get_logger() -> logging.Logger:
    """获取底层logger对象"""
    return log_manager.logger


# 提供便捷的日志函数
def debug(message: str):
    """记录调试信息的便捷函数"""
    log_manager.debug(message)


def info(message: str):
    """记录一般信息的便捷函数"""
    log_manager.info(message)


def warning(message: str):
    """记录警告信息的便捷函数"""
    log_manager.warning(message)


def error(message: str):
    """记录错误信息的便捷函数"""
    log_manager.error(message)


def critical(message: str):
    """记录严重错误信息的便捷函数"""
    log_manager.critical(message)