from utils.llms import get_llm
from utils.config import Config


# Author:@南哥AGI研习社 (B站 or YouTube 搜索“南哥AGI研习社”)


# 调用get_llm函数初始化Chat模型实例和Embedding模型实例
llm_chat, llm_embedding = get_llm(Config.LLM_TYPE)

# # 测试非流式输出
# response = llm_chat.invoke("天空是什么颜色?")
# print(response.content)
# print(response.response_metadata)

# 测试流式输出
chunks = []
for chunk in llm_chat.stream("天空是什么颜色?"):
    chunks.append(chunk)
    print(chunk.content, end="|", flush=True)










