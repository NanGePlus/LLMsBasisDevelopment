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

    # 大模型配置相关
    # openai:调用gpt模型；oneapi:调用oneapi方案支持的模型；qwen:调用阿里通义千问大模型；ollama:调用本地开源大模型
    LLM_TYPE = "openai"
    # 代理方式 国内外大模型
    OPENAI_API_BASE = "https://nangeai.top/v1"
    OPENAI_API_KEY = "sk-qqzZO0rjALbvkRXGwNNJp7q3lEtFja03zRx2H0iU6r3Sb2aq"
    OPENAI_CHAT_MODEL = "o3-mini-all"
    OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
    # OneAPI方式 国内外大模型(阿里通义千问为例)
    ONEAPI_API_BASE = "http://139.224.72.218:3000/v1"
    ONEAPI_API_KEY = "sk-OLpmUgKiUiAPYHfuB2B6Ce4e2dDc4e3398Cb63CcFa2f5371"
    ONEAPI_CHAT_MODEL = "qwen-turbo"
    ONEAPI_EMBEDDING_MODEL = "text-embedding-v1"
    # 大模型厂商原生接口 阿里通义千问为例
    QWEN_API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_API_KEY = "sk-7554c417a8d64930a64f751790edc417"
    QWEN_CHAT_MODEL = "qwen-turbo"
    QWEN_EMBEDDING_MODEL = "text-embedding-v1"
    # Ollama方式 本地开源大模型
    OLLAMA_API_BASE = "http://localhost:11434/v1"
    OLLAMA_API_KEY = "ollama"
    OLLAMA_CHAT_MODEL = "deepseek-r1:14b"
    OLLAMA_EMBEDDING_MODEL = "nomic-embed-text:latest"

    # 对文件进行文本预处理后灌库相关配置
    # 设置待处理的文件内容文类型，中文或英文
    TEXT_LANGUAGE = 'Chinese' # TEXT_LANGUAGE = 'English'
    INPUT_PDF = "input/健康档案.pdf" # INPUT_PDF = "input/DeepSeek_R1.pdf"
    # 指定文件中待处理的页码，全部页码则填None
    PAGE_NUMBERS = None # PAGE_NUMBERS = [2, 3]
    # chromaDB向量数据库的持久化存储文件夹路径
    CHROMADB_DIRECTORY = "chromaDB"
    # 待查询的chromaDB向量数据库的集合名称
    CHROMADB_COLLECTION_NAME = "demo001"
    # re-rank模型设置相关 根据自己的实际情况进行调整
    RERANK_MODEL = 'other/models/bge-reranker-large'

    # API服务地址和端口
    HOST = "0.0.0.0"
    PORT = 8012