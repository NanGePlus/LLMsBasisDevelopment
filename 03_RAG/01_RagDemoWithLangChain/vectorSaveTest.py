import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler
from openai import OpenAI
import chromadb
import uuid
from utils.config import Config
from utils.pdfSplitTestCh import getParagraphsCh
from utils.pdfSplitTestEn import getParagraphsEn



# Author:@南哥AGI研习社 (B站 or YouTube 搜索“南哥AGI研习社”)


# # 设置日志基本配置，级别为DEBUG或INFO
logger = logging.getLogger(__name__)
# 设置日志器级别为DEBUG
logger.setLevel(logging.DEBUG)
# logger.setLevel(logging.INFO)
logger.handlers = []  # 清空默认处理器
# 使用ConcurrentRotatingFileHandler
handler = ConcurrentRotatingFileHandler(
    # 日志文件
    Config.LOG_FILE,
    # 日志文件最大允许大小为5MB，达到上限后触发轮转
    maxBytes = Config.MAX_BYTES,
    # 在轮转时，最多保留3个历史日志文件
    backupCount = Config.BACKUP_COUNT
)
# 设置处理器级别为DEBUG
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
logger.addHandler(handler)


# get_embeddings方法计算向量
def get_embeddings(texts):
    if Config.LLM_TYPE == 'oneapi':
        try:
            client = OpenAI(
                base_url=Config.ONEAPI_API_BASE,
                api_key=Config.ONEAPI_API_KEY
            )
            data = client.embeddings.create(input=texts,model=Config.ONEAPI_EMBEDDING_MODEL).data
            return [x.embedding for x in data]
        except Exception as e:
            logger.info(f"生成向量时出错: {e}")
            return []
    elif Config.LLM_TYPE == 'qwen':
        try:
            client = OpenAI(
                base_url=Config.QWEN_API_BASE,
                api_key=Config.QWEN_API_KEY
            )
            data = client.embeddings.create(input=texts,model=Config.QWEN_EMBEDDING_MODEL).data
            return [x.embedding for x in data]
        except Exception as e:
            logger.info(f"生成向量时出错: {e}")
            return []
    elif Config.LLM_TYPE == 'ollama':
        try:
            client = OpenAI(
                base_url=Config.OLLAMA_API_BASE,
                api_key=Config.OLLAMA_API_KEY
            )
            data = client.embeddings.create(input=texts,model=Config.OLLAMA_EMBEDDING_MODEL).data
            return [x.embedding for x in data]
        except Exception as e:
            logger.info(f"生成向量时出错: {e}")
            return []
    else:
        try:
            client = OpenAI(
                base_url=Config.OPENAI_API_BASE,
                api_key=Config.OPENAI_API_KEY
            )
            data = client.embeddings.create(input=texts,model=Config.OPENAI_EMBEDDING_MODEL).data
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
        # 实例化一个chromadb对象
        # 设置一个文件夹进行向量数据库的持久化存储  路径为当前文件夹下chromaDB文件夹
        chroma_client = chromadb.PersistentClient(path=Config.CHROMADB_DIRECTORY)
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
    # 测试中文文本
    if Config.TEXT_LANGUAGE == 'Chinese':
        # 1、获取处理后的文本数据
        # 演示测试对指定的全部页进行处理，其返回值为划分为段落的文本列表
        paragraphs = getParagraphsCh(
            filename=Config.INPUT_PDF,
            page_numbers=Config.PAGE_NUMBERS,
            min_line_length=1
        )
        # 2、将文本片段灌入向量数据库
        # 实例化一个向量数据库对象
        # 其中，传参collection_name为集合名称, embedding_fn为向量处理函数
        vector_db = MyVectorDBConnector(Config.CHROMADB_COLLECTION_NAME, generate_vectors)
        # 向向量数据库中添加文档（文本数据、文本数据对应的向量数据）
        vector_db.add_documents(paragraphs)
        # 3、封装检索接口进行检索测试
        user_query = "张三九的基本信息是什么"
        # 将检索出的5个近似的结果
        search_results = vector_db.search(user_query, 5)
        logger.info(f"检索向量数据库的结果: {search_results}")
    # 测试英文文本
    elif Config.TEXT_LANGUAGE == 'English':
        # 1、获取处理后的文本数据
        # 演示测试对指定的全部页进行处理，其返回值为划分为段落的文本列表
        paragraphs = getParagraphsEn(
            filename=Config.INPUT_PDF,
            page_numbers=Config.PAGE_NUMBERS,
            min_line_length=1
        )
        # 2、将文本片段灌入向量数据库
        # 实例化一个向量数据库对象
        # 其中，传参collection_name为集合名称, embedding_fn为向量处理函数
        vector_db = MyVectorDBConnector(Config.CHROMADB_COLLECTION_NAME, generate_vectors)
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

