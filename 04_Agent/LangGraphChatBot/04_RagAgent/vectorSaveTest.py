# 功能说明：将PDF文件进行向量计算并持久化存储到向量数据库（chroma）
import logging
from openai import OpenAI
import chromadb
import uuid
from utils import pdfSplitTest_Ch
from utils import pdfSplitTest_En




# 设置日志模版
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# GPT大模型 OpenAI相关配置
OPENAI_API_BASE = "https://nangeai.top/v1"
OPENAI_EMBEDDING_API_KEY = "sk-aR2Y17PuOKtS3455PbrKSKPswr047o6AMvCG6g3EfViPku"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
# 国产大模型 OneAPI相关配置,通义千问为例
ONEAPI_API_BASE = "http://139.224.72.218:3000/v1"
ONEAPI_EMBEDDING_API_KEY = "sk-GseYmJ8pX1D4I32323506e8fDf514a51A3C4B714FfD45aD9"
ONEAPI_EMBEDDING_MODEL = "text-embedding-v1"
# 阿里通义千问大模型
QWen_API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWen_EMBEDDING_API_KEY = "sk-c89db4d8628323232846e144c9a537f"
QWen_EMBEDDING_MODEL = "text-embedding-v1"
# 本地开源大模型 Ollama方式,nomic-embed-text为例
OLLAMA_API_BASE = "http://localhost:11434/v1"
OLLAMA_EMBEDDING_API_KEY = "ollama"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text:latest"


# openai:调用gpt模型,oneapi:调用oneapi方案支持的模型,ollama:调用本地开源大模型,qwen:调用阿里通义千问大模型
llmType = "openai"

# 设置测试文本类型 Chinese 或 English
TEXT_LANGUAGE = 'Chinese'
INPUT_PDF = "input/健康档案.pdf"
# TEXT_LANGUAGE = 'English'
# INPUT_PDF = "input/DeepSeek_R1.pdf"

# 指定文件中待处理的页码，全部页码则填None
PAGE_NUMBERS=None
# PAGE_NUMBERS=[2, 3]

# 指定向量数据库chromaDB的存储位置和集合 根据自己的实际情况进行调整
CHROMADB_DIRECTORY = "chromaDB"  # chromaDB向量数据库的持久化路径
CHROMADB_COLLECTION_NAME = "demo001"  # 待查询的chromaDB向量数据库的集合名称


# get_embeddings方法计算向量
def get_embeddings(texts):
    global llmType
    global ONEAPI_API_BASE, ONEAPI_EMBEDDING_API_KEY, ONEAPI_EMBEDDING_MODEL
    global OPENAI_API_BASE, OPENAI_EMBEDDING_API_KEY, OPENAI_EMBEDDING_MODEL
    global QWen_API_BASE, QWen_EMBEDDING_API_KEY, QWen_EMBEDDING_MODEL
    global OLLAMA_API_BASE, OLLAMA_EMBEDDING_API_KEY, OLLAMA_EMBEDDING_MODEL
    if llmType == 'oneapi':
        try:
            client = OpenAI(
                base_url=ONEAPI_API_BASE,
                api_key=ONEAPI_EMBEDDING_API_KEY
            )
            data = client.embeddings.create(input=texts,model=ONEAPI_EMBEDDING_MODEL).data
            return [x.embedding for x in data]
        except Exception as e:
            logger.info(f"生成向量时出错: {e}")
            return []
    elif llmType == 'qwen':
        try:
            client = OpenAI(
                base_url=QWen_API_BASE,
                api_key=QWen_EMBEDDING_API_KEY
            )
            data = client.embeddings.create(input=texts,model=QWen_EMBEDDING_MODEL).data
            return [x.embedding for x in data]
        except Exception as e:
            logger.info(f"生成向量时出错: {e}")
            return []
    elif llmType == 'ollama':
        try:
            client = OpenAI(
                base_url=OLLAMA_API_BASE,
                api_key=OLLAMA_EMBEDDING_API_KEY
            )
            data = client.embeddings.create(input=texts,model=OLLAMA_EMBEDDING_MODEL).data
            return [x.embedding for x in data]
        except Exception as e:
            logger.info(f"生成向量时出错: {e}")
            return []
    else:
        try:
            client = OpenAI(
                base_url=OPENAI_API_BASE,
                api_key=OPENAI_EMBEDDING_API_KEY
            )
            data = client.embeddings.create(input=texts,model=OPENAI_EMBEDDING_MODEL).data
            return [x.embedding for x in data]
        except Exception as e:
            logger.info(f"生成向量时出错: {e}")
            return []


# 对文本按批次进行向量计算
def generate_vectors(data, max_batch_size=25):
    results = []
    for i in range(0, len(data), max_batch_size):
        batch = data[i:i + max_batch_size]
        # 调用向量生成get_embeddings方法  根据调用的API不同进行选择
        response = get_embeddings(batch)
        results.extend(response)
    return results


# 封装向量数据库chromadb类，提供两种方法
class MyVectorDBConnector:
    def __init__(self, collection_name, embedding_fn):
        # 申明使用全局变量
        global CHROMADB_DIRECTORY
        # 实例化一个chromadb对象
        # 设置一个文件夹进行向量数据库的持久化存储  路径为当前文件夹下chromaDB文件夹
        chroma_client = chromadb.PersistentClient(path=CHROMADB_DIRECTORY)
        # 创建一个collection数据集合
        # get_or_create_collection()获取一个现有的向量集合，如果该集合不存在，则创建一个新的集合
        self.collection = chroma_client.get_or_create_collection(
            name=collection_name)
        # embedding处理函数
        self.embedding_fn = embedding_fn

    # 添加文档到集合
    # 文档通常包括文本数据和其对应的向量表示，这些向量可以用于后续的搜索和相似度计算
    def add_documents(self, documents):
        self.collection.add(
            embeddings=self.embedding_fn(documents),  # 调用函数计算出文档中文本数据对应的向量
            documents=documents,  # 文档的文本数据
            ids=[str(uuid.uuid4()) for i in range(len(documents))]  # 文档的唯一标识符 自动生成uuid,128位  
        )
        
    # 检索向量数据库，返回包含查询结果的对象或列表，这些结果包括最相似的向量及其相关信息
    # query：查询文本
    # top_n：返回与查询向量最相似的前 n 个向量
    def search(self, query, top_n):
        try:
            results = self.collection.query(
                # 计算查询文本的向量，然后将查询文本生成的向量在向量数据库中进行相似度检索
                query_embeddings=self.embedding_fn([query]),
                n_results=top_n
            )
            return results
        except Exception as e:
            logger.info(f"检索向量数据库时出错: {e}")
            return []


# 封装文本预处理及灌库方法  提供外部调用
def vectorStoreSave():
    global TEXT_LANGUAGE, CHROMADB_COLLECTION_NAME, INPUT_PDF, PAGE_NUMBERS

    # 测试中文文本
    if TEXT_LANGUAGE == 'Chinese':
        # 1、获取处理后的文本数据
        # 演示测试对指定的全部页进行处理，其返回值为划分为段落的文本列表
        paragraphs = pdfSplitTest_Ch.getParagraphs(
            filename=INPUT_PDF,
            page_numbers=PAGE_NUMBERS,
            min_line_length=1
        )
        # 2、将文本片段灌入向量数据库
        # 实例化一个向量数据库对象
        # 其中，传参collection_name为集合名称, embedding_fn为向量处理函数
        vector_db = MyVectorDBConnector(CHROMADB_COLLECTION_NAME, generate_vectors)
        # 向向量数据库中添加文档（文本数据、文本数据对应的向量数据）
        vector_db.add_documents(paragraphs)
        # 3、封装检索接口进行检索测试
        user_query = "张三九的基本信息是什么"
        # 将检索出的5个近似的结果
        search_results = vector_db.search(user_query, 5)
        logger.info(f"检索向量数据库的结果: {search_results}")

    # 测试英文文本
    elif TEXT_LANGUAGE == 'English':
        # 1、获取处理后的文本数据
        # 演示测试对指定的全部页进行处理，其返回值为划分为段落的文本列表
        paragraphs = pdfSplitTest_En.getParagraphs(
            filename=INPUT_PDF,
            page_numbers=PAGE_NUMBERS,
            min_line_length=1
        )
        # 2、将文本片段灌入向量数据库
        # 实例化一个向量数据库对象
        # 其中，传参collection_name为集合名称, embedding_fn为向量处理函数
        vector_db = MyVectorDBConnector(CHROMADB_COLLECTION_NAME, generate_vectors)
        # 向向量数据库中添加文档（文本数据、文本数据对应的向量数据）
        vector_db.add_documents(paragraphs)
        # 3、封装检索接口进行检索测试
        user_query = "deepseek-r1性能如何？"
        # 将检索出的5个近似的结果
        search_results = vector_db.search(user_query, 5)
        logger.info(f"检索向量数据库的结果: {search_results}")


if __name__ == "__main__":
    # 测试文本预处理及灌库
    vectorStoreSave()

