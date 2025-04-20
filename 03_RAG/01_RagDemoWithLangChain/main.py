import os
import re
import json
import uuid
import time
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn
import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler
from utils.llms import get_llm
from utils.config import Config



# Author:@南哥AGI研习社 (B站 or YouTube 搜索“南哥AGI研习社”)


# 设置LangSmith环境变量 进行应用跟踪，实时了解应用中的每一步发生了什么
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_API_KEY"] = "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"

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


# 定义消息类，用于封装API接口返回数据
# 定义Message类
class Message(BaseModel):
    role: str
    content: str
# 定义ChatCompletionRequest类
class ChatCompletionRequest(BaseModel):
    messages: List[Message]
    stream: Optional[bool] = False
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
# 定义ChatCompletionResponseChoice类
class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: Message
    finish_reason: Optional[str] = None
# 定义ChatCompletionResponse类
class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    choices: List[ChatCompletionResponseChoice]
    system_fingerprint: Optional[str] = None


# 获取prompt在chain中传递的prompt最终的内容
def getPrompt(prompt):
    logger.info(f"最后给到LLM的prompt的内容: {prompt}")
    return prompt


# 格式化响应，对输入的文本进行段落分隔、添加适当的换行符，以及在代码块中增加标记，以便生成更具可读性的输出
def format_response(response):
    # 使用正则表达式 \n{2, }将输入的response按照两个或更多的连续换行符进行分割。这样可以将文本分割成多个段落，每个段落由连续的非空行组成
    paragraphs = re.split(r'\n{2,}', response)
    # 空列表，用于存储格式化后的段落
    formatted_paragraphs = []
    # 遍历每个段落进行处理
    for para in paragraphs:
        # 检查段落中是否包含代码块标记
        if '```' in para:
            # 将段落按照```分割成多个部分，代码块和普通文本交替出现
            parts = para.split('```')
            for i, part in enumerate(parts):
                # 检查当前部分的索引是否为奇数，奇数部分代表代码块
                if i % 2 == 1:  # 这是代码块
                    # 将代码块部分用换行符和```包围，并去除多余的空白字符
                    parts[i] = f"\n```\n{part.strip()}\n```\n"
            # 将分割后的部分重新组合成一个字符串
            para = ''.join(parts)
        else:
            # 否则，将句子中的句点后面的空格替换为换行符，以便句子之间有明确的分隔
            para = para.replace('. ', '.\n')
        # 将格式化后的段落添加到formatted_paragraphs列表
        # strip()方法用于移除字符串开头和结尾的空白字符（包括空格、制表符 \t、换行符 \n等）
        formatted_paragraphs.append(para.strip())
    # 将所有格式化后的段落用两个换行符连接起来，以形成一个具有清晰段落分隔的文本
    return '\n\n'.join(formatted_paragraphs)


# 定义了一个异步函数lifespan，它接收一个FastAPI应用实例app作为参数。这个函数将管理应用的生命周期，包括启动和关闭时的操作
# 函数在应用启动时执行一些初始化操作，如加载上下文数据、以及初始化问题生成器
# 函数在应用关闭时执行一些清理操作
# @asynccontextmanager 装饰器用于创建一个异步上下文管理器，它允许你在 yield 之前和之后执行特定的代码块，分别表示启动和关闭时的操作
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    # 申明引用全局变量，在函数中被初始化，并在整个应用中使用
    global chat_model, llm_embedding, retriever, prompt, chain
    try:
        logger.info("正在初始化Chat模型、Embeddimg模型、提取prompt模版、定义retriever、定义chain...")
        #（1）初始化LLM
        # 调用get_llm函数初始化Chat模型实例和Embedding模型实例
        chat_model, llm_embedding = get_llm(Config.LLM_TYPE)
        #（2）实例化Chroma对象 根据自己的实际情况调整persist_directory和collection_name
        vectorstore = Chroma(persist_directory=Config.CHROMADB_DIRECTORY,
                             collection_name=Config.CHROMADB_COLLECTION_NAME,
                             embedding_function=llm_embedding,
                             )
        #（3）提取prompt模版
        prompt_template_system = PromptTemplate.from_file(Config.PROMPT_TEMPLATE_TXT_SYS)
        prompt_template_user = PromptTemplate.from_file(Config.PROMPT_TEMPLATE_TXT_USER)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system",prompt_template_system.template),
                ("human", prompt_template_user.template)
            ]
        )
        #（4）定义retriever
        # 将RAG检索放到LangChain的LCEL的chain中执行
        # 这段代码是使用Langchain框架中的`as_retriever`方法创建一个检索器对象
        # LangChain VectorStore对象不是 Runnable 的子类，因此无法集成到LangChain的LCEL的chain中
        # LangChain Retrievers是Runnable，实现了一组标准方法可集成到LCEL的chain中
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3},
        )
        #（5）定义chain
        chain = (
                {"query": RunnablePassthrough(),"context": retriever}
                | prompt
                | getPrompt
                | chat_model
                | StrOutputParser()
        )
        logger.info("初始化完成")
    except Exception as e:
        logger.error(f"初始化过程中出错: {str(e)}")
        # raise 关键字重新抛出异常，以确保程序不会在错误状态下继续运行
        raise

    # yield 关键字将控制权交还给FastAPI框架，使应用开始运行
    # 分隔了启动和关闭的逻辑。在yield 之前的代码在应用启动时运行，yield 之后的代码在应用关闭时运行
    yield
    # 关闭时执行
    logger.info("正在关闭...")


# lifespan参数用于在应用程序生命周期的开始和结束时执行一些初始化或清理工作
app = FastAPI(lifespan=lifespan)


# 封装POST请求接口，与大模型进行问答
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    # 申明引用全局变量，在函数中被初始化，并在整个应用中使用
    if not chat_model or not llm_embedding or not retriever or not prompt or not chain:
        logger.error("服务未初始化")
        raise HTTPException(status_code=500, detail="服务未初始化")

    try:
        logger.info(f"收到聊天完成请求: {request}")
        query_prompt = request.messages[-1].content
        logger.info(f"用户问题是: {query_prompt}")

        # 处理流式响应
        if request.stream:
            async def generate_stream():
                chunk_id = f"chatcmpl-{uuid.uuid4().hex}"
                # async for chunk in with_message_history.astream(
                for chunk in chain.stream(query_prompt):
                    # 在处理过程中产生每个块
                    yield f"data: {json.dumps({'id': chunk_id,'object': 'chat.completion.chunk','created': int(time.time()),'choices': [{'index': 0,'delta': {'content': chunk},'finish_reason': None}]})}\n\n"
                # 流结束的最后一块
                yield f"data: {json.dumps({'id': chunk_id,'object': 'chat.completion.chunk','created': int(time.time()),'choices': [{'index': 0,'delta': {},'finish_reason': 'stop'}]})}\n\n"
            # 返回fastapi.responses中StreamingResponse对象
            return StreamingResponse(generate_stream(), media_type="text/event-stream")

        # 处理非流式响应处理
        else:
            # 调用chain进行查询
            result = chain.invoke(query_prompt)
            formatted_response = str(format_response(result))
            logger.info(f"格式化的搜索结果: {formatted_response}")

            response = ChatCompletionResponse(
                choices=[
                    ChatCompletionResponseChoice(
                        index=0,
                        message=Message(role="assistant", content=formatted_response),
                        finish_reason="stop"
                    )
                ]
            )
            logger.info(f"发送响应内容: \n{response}")
            # 返回fastapi.responses中JSONResponse对象
            # model_dump()方法通常用于将Pydantic模型实例的内容转换为一个标准的Python字典，以便进行序列化
            return JSONResponse(content=response.model_dump())

    except Exception as e:
        logger.error(f"处理聊天完成时出错:\n\n {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    logger.info(f"在端口 {Config.PORT} 上启动服务器")
    # uvicorn是一个用于运行ASGI应用的轻量级、超快速的ASGI服务器实现
    # 用于部署基于FastAPI框架的异步PythonWeb应用程序
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)


