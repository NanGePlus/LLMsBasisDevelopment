# 导入操作系统接口模块，用于处理文件路径和环境变量
import os
# 用于正则表达式匹配和处理字符串
import re
# 用于JSON数据的序列化和反序列化
import json
# 用于定义异步上下文管理器
from contextlib import asynccontextmanager
# 用于类型提示，定义列表和可选参数
from typing import List, Tuple
# 用于创建Web应用和处理HTTP异常
from fastapi import FastAPI, HTTPException, Depends
# 用于返回JSON和流式响应
from fastapi.responses import JSONResponse, StreamingResponse
# 用于运行FastAPI应用
import uvicorn
# 导入日志模块，用于记录程序运行时的信息
import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler
# 导入系统模块，用于处理系统相关的操作，如退出程序
import sys
import time
# 导入UUID模块，用于生成唯一标识符
import uuid
# 从typing模块导入类型提示工具
from typing import Optional
# 导入Pydantic的基类和字段定义工具
from pydantic import BaseModel, Field
# 从自定义的库中引入函数
from demoRagAgent import (
    ToolConfig,
    create_graph,
    save_graph_visualization,
    get_llm,
    get_tools,
    Config,
    ConnectionPool,
    ConnectionPoolError,
    monitor_connection_pool,
)



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
    userId: Optional[str] = None
    conversationId: Optional[str] = None

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


def format_response(response):
    """对输入的文本进行段落分隔、添加适当的换行符，以及在代码块中增加标记，以便生成更具可读性的输出。

    Args:
        response: 输入的文本。

    Returns:
        具有清晰段落分隔的文本。
    """
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


# 管理 FastAPI 应用生命周期的异步上下文管理器，负责启动和关闭时的初始化与清理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    管理 FastAPI 应用生命周期的异步上下文管理器，负责启动和关闭时的初始化与清理。

    Args:
        app (FastAPI): FastAPI 应用实例。

    Yields:
        None: 在 yield 前完成初始化，yield 后执行清理。

    Raises:
        ConnectionPoolError: 数据库连接池初始化或操作失败时抛出。
        Exception: 其他未预期的异常。
    """
    # 声明全局变量 graph 和 tool_config
    global graph, tool_config
    # 初始化数据库连接池为 None
    db_connection_pool = None
    try:
        # 调用 get_llm 初始化聊天模型和嵌入模型
        llm_chat, llm_embedding = get_llm(Config.LLM_TYPE)

        # 获取工具列表，基于嵌入模型
        tools = get_tools(llm_embedding)

        # 创建工具配置实例
        tool_config = ToolConfig(tools)

        # 定义数据库连接参数：自动提交、无预准备阈值、5秒超时
        connection_kwargs = {"autocommit": True, "prepare_threshold": 0, "connect_timeout": 5}
        # 创建数据库连接池：最大20个连接，最小2个活跃连接，超时10秒
        db_connection_pool = ConnectionPool(
            conninfo=Config.DB_URI,
            max_size=20,
            min_size=2,
            kwargs=connection_kwargs,
            timeout=10
        )

        # 尝试打开数据库连接池
        try:
            # 打开连接池以启用数据库连接
            db_connection_pool.open()
            # 记录连接池初始化成功的日志（INFO 级别）
            logger.info("Database connection pool initialized")
            # 记录详细调试日志（DEBUG 级别）
            logger.debug("Database connection pool initialized")
        except Exception as e:
            # 记录连接池打开失败的错误日志
            logger.error(f"Failed to open connection pool: {e}")
            # 抛出自定义连接池异常
            raise ConnectionPoolError(f"无法打开数据库连接池: {str(e)}")

        # 启动连接池监控线程，60秒检查一次，设置为守护线程
        monitor_thread = monitor_connection_pool(db_connection_pool, interval=60)

        # 尝试创建状态图
        try:
            # 使用数据库连接池和模型创建状态图
            graph = create_graph(db_connection_pool, llm_chat, llm_embedding, tool_config)
        except ConnectionPoolError as e:
            # 记录状态图创建失败的错误日志
            logger.error(f"Graph creation failed: {e}")
            # 退出程序，返回状态码 1
            sys.exit(1)

        # 保存状态图的可视化表示
        save_graph_visualization(graph)

    except ConnectionPoolError as e:
        # 捕获并记录连接池相关异常
        logger.error(f"Connection pool error: {e}")
        # 退出程序，返回状态码 1
        sys.exit(1)
    except Exception as e:
        # 捕获并记录其他未预期的异常
        logger.error(f"Unexpected error: {e}")
        # 退出程序，返回状态码 1
        sys.exit(1)

    # yield 表示应用运行期间，初始化完成后进入运行状态
    yield
    # 检查并关闭数据库连接池（清理资源）
    if db_connection_pool and not db_connection_pool.closed:
        # 关闭连接池
        db_connection_pool.close()
        # 记录连接池关闭的日志
        logger.info("Database connection pool closed")
    # 记录服务关闭的日志
    logger.info("The service has been shut down")

# 创建FastAPI实例 lifespan参数用于在应用程序生命周期的开始和结束时执行一些初始化或清理工作
app = FastAPI(lifespan=lifespan)


# 处理非流式响应的异步函数，生成并返回完整的响应内容
async def handle_non_stream_response(user_input, graph, tool_config, config):
    """
    处理非流式响应的异步函数，生成并返回完整的响应内容。

    Args:
        user_input (str): 用户输入的内容。
        graph: 图对象，用于处理消息流。
        tool_config: 工具配置对象，包含可用工具的名称和定义。
        config (dict): 配置参数，包含线程和用户标识。

    Returns:
        JSONResponse: 包含格式化响应的 JSON 响应对象。
    """
    # 初始化 content 变量，用于存储最终响应内容
    content = None
    try:
        # 启动 graph.stream 处理用户输入，生成事件流
        events = graph.stream({"messages": [{"role": "user", "content": user_input}], "rewrite_count": 0}, config)
        # 遍历事件流中的每个事件
        for event in events:
            # 遍历事件中的所有值
            for value in event.values():
                # 检查事件值是否包含有效消息列表
                if "messages" not in value or not isinstance(value["messages"], list):
                    # 记录警告日志，跳过无效消息
                    logger.warning("No valid messages in response")
                    continue

                # 获取消息列表中的最后一条消息
                last_message = value["messages"][-1]

                # 检查消息是否包含工具调用
                if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                    # 遍历所有工具调用
                    for tool_call in last_message.tool_calls:
                        # 验证工具调用是否为字典且包含名称
                        if isinstance(tool_call, dict) and "name" in tool_call:
                            # 记录工具调用日志
                            logger.info(f"Calling tool: {tool_call['name']}")
                    # 跳过本次循环，继续处理下一事件
                    continue

                # 检查消息是否包含内容
                if hasattr(last_message, "content"):
                    # 将消息内容赋值给 content
                    content = last_message.content

                    # 检查是否为工具输出（基于工具名称）
                    if hasattr(last_message, "name") and last_message.name in tool_config.get_tool_names():
                        # 获取工具名称
                        tool_name = last_message.name
                        # 记录工具输出日志
                        logger.info(f"Tool Output [{tool_name}]: {content}")
                    # 处理大模型输出（非工具消息）
                    else:
                        # 记录最终响应日志
                        logger.info(f"Final Response is: {content}")
                else:
                    # 记录无内容的消息日志，跳过处理
                    logger.info("Message has no content, skipping")
    except ValueError as ve:
        # 捕获并记录值错误
        logger.error(f"Value error in response processing: {ve}")
    except Exception as e:
        # 捕获并记录其他未预期的异常
        logger.error(f"Error processing response: {e}")

    # 格式化响应内容，若无内容则返回默认值
    formatted_response = str(format_response(content)) if content else "No response generated"
    # 记录格式化后的响应日志
    logger.info(f"Results for Formatting: {formatted_response}")

    # 构造返回给客户端的响应对象
    try:
        response = ChatCompletionResponse(
            choices=[
                ChatCompletionResponseChoice(
                    index=0,
                    message=Message(role="assistant", content=formatted_response),
                    finish_reason="stop"
                )
            ]
        )
    except Exception as resp_error:
        # 捕获并记录构造响应对象时的异常
        logger.error(f"Error creating response object: {resp_error}")
        # 构造错误响应对象
        response = ChatCompletionResponse(
            choices=[
                ChatCompletionResponseChoice(
                    index=0,
                    message=Message(role="assistant", content="Error generating response"),
                    finish_reason="error"
                )
            ]
        )

    # 记录发送给客户端的响应内容日志
    logger.info(f"Send response content: \n{response}")
    # 返回 JSON 格式的响应对象
    return JSONResponse(content=response.model_dump())


# 处理流式响应的异步函数，生成并返回流式数据
async def handle_stream_response(user_input, graph, config):
    """
    处理流式响应的异步函数，生成并返回流式数据。

    Args:
        user_input (str): 用户输入的内容。
        graph: 图对象，用于处理消息流。
        config (dict): 配置参数，包含线程和用户标识。

    Returns:
        StreamingResponse: 流式响应对象，媒体类型为 text/event-stream。
    """
    async def generate_stream():
        """
        内部异步生成器函数，用于产生流式响应数据。

        Yields:
            str: 流式数据块，格式为 SSE (Server-Sent Events)。

        Raises:
            Exception: 流生成过程中可能抛出的异常。
        """
        try:
            # 生成唯一的 chunk ID
            chunk_id = f"chatcmpl-{uuid.uuid4().hex}"
            # 调用 graph.stream 获取消息流
            stream_data = graph.stream(
                {"messages": [{"role": "user", "content": user_input}], "rewrite_count": 0},
                config,
                stream_mode="messages"
            )
            # 遍历消息流中的每个数据块
            for message_chunk, metadata in stream_data:
                try:
                    # 获取当前节点名称
                    node_name = metadata.get("langgraph_node") if metadata else None
                    # 仅处理 generate 和 agent 节点
                    if node_name in ["generate", "agent"]:
                        # 获取消息内容，默认空字符串
                        chunk = getattr(message_chunk, 'content', '')
                        # 记录流式数据块日志
                        logger.info(f"Streaming chunk from {node_name}: {chunk}")
                        # 产出流式数据块
                        yield f"data: {json.dumps({'id': chunk_id, 'object': 'chat.completion.chunk', 'created': int(time.time()), 'choices': [{'index': 0, 'delta': {'content': chunk}, 'finish_reason': None}]})}\n\n"
                except Exception as chunk_error:
                    # 记录单个数据块处理异常
                    logger.error(f"Error processing stream chunk: {chunk_error}")
                    continue

            # 产出流结束标记
            yield f"data: {json.dumps({'id': chunk_id, 'object': 'chat.completion.chunk', 'created': int(time.time()), 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
        except Exception as stream_error:
            # 记录流生成过程中的异常
            logger.error(f"Stream generation error: {stream_error}")
            # 产出错误提示
            yield f"data: {json.dumps({'error': 'Stream processing failed'})}\n\n"

    # 返回流式响应对象
    return StreamingResponse(generate_stream(), media_type="text/event-stream")


# 依赖注入函数，用于获取 graph 和 tool_config
async def get_dependencies() -> Tuple[any, any]:
    """
    依赖注入函数，用于获取 graph 和 tool_config。

    Returns:
        Tuple: 包含 (graph, tool_config) 的元组。

    Raises:
        HTTPException: 如果 graph 或 tool_config 未初始化，则抛出 500 错误。
    """
    if not graph or not tool_config:
        raise HTTPException(status_code=500, detail="Service not initialized")
    return graph, tool_config


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest, dependencies: Tuple[any, any] = Depends(get_dependencies)):
    """接收来自前端的请求数据进行业务的处理。

    Args:
        request: 请求参数。

    Returns:
        标准的Python字典。
    """
    try:
        graph, tool_config = dependencies
        # 检查request是否有效
        if not request.messages or not request.messages[-1].content:
            logger.error("Invalid request: Empty or invalid messages")
            raise HTTPException(status_code=400, detail="Messages cannot be empty or invalid")
        user_input = request.messages[-1].content
        logger.info(f"The user's user_input is: {user_input}")

        # 定义运行时配置，包含线程ID和用户ID，使用默认值防止未定义
        config = {
            "configurable": {
                "thread_id": f"{getattr(request, 'userId', 'unknown')}@@{getattr(request, 'conversationId', 'default')}",
                "user_id": getattr(request, 'userId', 'unknown')
            }
        }

        # 调用流式输出
        if request.stream:
            return await handle_stream_response(user_input, graph, config)
        # 调用非流式输出
        return await handle_non_stream_response(user_input, graph, tool_config, config)

    except Exception as e:
        logger.error(f"Error handling chat completion:\n\n {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logger.info(f"Start the server on port {Config.PORT}")
    # uvicorn是一个用于运行ASGI应用的轻量级、超快速的ASGI服务器实现
    # 用于部署基于FastAPI框架的异步PythonWeb应用程序
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)


