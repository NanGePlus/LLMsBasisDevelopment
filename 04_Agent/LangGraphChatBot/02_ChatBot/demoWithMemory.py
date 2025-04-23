import os
import uuid
from langgraph.store.base import BaseStore
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END, MessagesState
from llms import get_llm
import sys
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore



# openai:调用gpt模型,oneapi:调用oneapi方案支持的模型,ollama:调用本地开源大模型,qwen:调用阿里通义千问大模型
llm_type = "openai"


# 创建和配置chatbot的状态图
def create_graph(llm_type: str) -> StateGraph:
    try:
        # 初始化LLM
        llm, embedding = get_llm(llm_type)

        # 初始化MemoryStore
        in_memory_store = InMemoryStore(
            index={
                "embed": embedding,
                "dims": 1536,
            }
        )

        # 构建graph
        graph_builder = StateGraph(MessagesState)

        # 自定义函数修剪和过滤state中的消息
        def filter_messages(messages: list):
            if len(messages) <= 3:
                return messages
            return messages[-3:]

        # 定义chatbot的node
        def chatbot(state: MessagesState, config: RunnableConfig, *, store: BaseStore):
            # 1、长期记忆逻辑
            # 设置命名空间 namespace
            namespace = ("memories", config["configurable"]["user_id"])
            # 获取state中最新一条消息(用户问题)进行检索
            memories = store.search(namespace, query=str(state["messages"][-1].content))
            info = "\n".join([d.value["data"] for d in memories])
            # 将检索到的知识拼接到系统prompt
            system_msg = f"You are a helpful assistant talking to the user. User info: {info}"
            # 获取state中的消息进行消息过滤后存储新的记忆
            last_message = state["messages"][-1]
            if "记住" in last_message.content.lower():
                memory = "我的频道是南哥AGI研习社。"
                store.put(namespace, str(uuid.uuid4()), {"data": memory})
            # 2、短期记忆逻辑 进行消息过滤
            messages = filter_messages(state["messages"])
            # 3、调用LLM
            response = llm.invoke(
                [{"role": "system", "content": system_msg}] + messages
            )
            return {"messages": [response]}

        # 配置graph
        graph_builder.add_node("chatbot", chatbot)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)

        # 这里使用内存存储 也可以持久化到数据库
        memory = MemorySaver()
        # 编译生成graph并返回
        return graph_builder.compile(checkpointer=memory, store=in_memory_store)

    except Exception as e:
        raise RuntimeError(f"Failed to create graph: {str(e)}")


# 将构建的graph可视化保存为 PNG 文件
def save_graph_visualization(graph: StateGraph, filename: str = "graph.png") -> None:
    try:
        with open(filename, "wb") as f:
            f.write(graph.get_graph().draw_mermaid_png())
        print(f"Graph visualization saved as {filename}")
    except IOError as e:
        print(f"Warning: Failed to save graph visualization: {str(e)}")


# 处理用户问题
def stream_response(graph: StateGraph, user_input: str, config) -> None:
    try:
        events = graph.stream({"messages": [{"role": "user", "content": user_input}]}, config)
        for event in events:
            for value in event.values():
                print("Assistant:", value["messages"][-1].content)
    except Exception as e:
        print(f"Error processing response: {str(e)}")


def main():
    try:
        graph = create_graph(llm_type)
        save_graph_visualization(graph)
    except RuntimeError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

    # 测试1
    config = {"configurable": {"thread_id": "1", "user_id": "1"}}
    input_message = {"role": "user", "content": "记住：我的频道是南哥AGI研习社"}
    for chunk in graph.stream({"messages": [input_message]}, config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()

    # 测试2
    config = {"configurable": {"thread_id": "2", "user_id": "1"}}
    input_message = {"role": "user", "content": "我的频道是什么?"}
    for chunk in graph.stream({"messages": [input_message]}, config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()

    # 测试3
    config = {"configurable": {"thread_id": "3", "user_id": "2"}}
    input_message = {"role": "user", "content": "我的频道是什么?"}
    for chunk in graph.stream({"messages": [input_message]}, config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()

    # 测试4
    print("Chatbot ready! Type 'quit', 'exit', or 'q' to end the conversation.")
    config = {"configurable": {"thread_id": "4", "user_id": "4"}}
    while True:
        try:
            user_input = input("User: ").strip()

            # 退出触发条件设置
            if user_input.lower() in {"quit", "exit", "q"}:
                print("Goodbye!")
                break

            if not user_input:
                print("Please enter something to chat about!")
                continue

            stream_response(graph, user_input, config)

        except KeyboardInterrupt:
            print("\nInterrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            fallback_input = "What do you know about LangGraph?"
            print(f"User (fallback): {fallback_input}")
            stream_response(graph, fallback_input)
            break


if __name__ == "__main__":
    main()