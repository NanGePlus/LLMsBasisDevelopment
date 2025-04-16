# config.py
import os

class Config:
    """统一的配置类，集中管理所有常量"""
    # prompt文件路径
    PROMPT_TEMPLATE_TXT_SYS = "prompt_template_system.txt"
    PROMPT_TEMPLATE_TXT_USER = "prompt_template_user.txt"

    # 日志持久化存储
    LOG_DIR = "output"
    LOG_FILE = os.path.join(LOG_DIR, "app.log")
    # 确保日志目录存在
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    MAX_BYTES=5*1024*1024,
    BACKUP_COUNT=3

    # openai:调用gpt模型,oneapi:调用oneapi方案支持的模型,qwen:调用阿里通义千问大模型,ollama:调用本地开源大模型
    LLM_TYPE = "openai"

    # API服务地址和端口
    HOST = "0.0.0.0"
    PORT = 8012