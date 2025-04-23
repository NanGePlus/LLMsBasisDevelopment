import gradio as gr
import requests
import json
import logging
import re


# Author:@南哥AGI研习社 (B站 or YouTube 搜索“南哥AGI研习社”)


# 设置日志模版
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 后端服务接口地址
url = "http://localhost:8012/v1/chat/completions"
headers = {"Content-Type": "application/json"}


# 默认流式输出 True or False
stream_flag = False


def send_message(user_message, history):
    # 封装请求的参数
    data = {
        "messages": [{"role": "user", "content": user_message}],
        "stream": stream_flag,
        "userId": "123",
        "conversationId": "123"
    }

    # 等待LLM产生token前的等待状态
    history = history + [["user", user_message], ["assistant", "正在生成回复..."]]
    yield history

    # 对deepseek-r1模型进行格式化处理
    def format_response(full_text):
        # 精确替换 <think> 和 </think>
        formatted_text = full_text
        formatted_text = re.sub(r'<think>', '**思考过程**：\n', formatted_text)
        formatted_text = re.sub(r'</think>', '\n\n**最终回复**：\n', formatted_text)
        # logger.info(f"formatted_text: {formatted_text}")
        return formatted_text.strip()

    # 流式输出
    if stream_flag:
        assistant_response = ""
        try:
            with requests.post(url, headers=headers, data=json.dumps(data), stream=True) as response:
                for line in response.iter_lines():
                    if line:
                        json_str = line.decode('utf-8').strip("data: ")
                        if not json_str:
                            logger.info(f"收到空字符串，跳过...")
                            continue
                        # logger.info(f"接收数据json_str:{json_str}")
                        if json_str.startswith('{') and json_str.endswith('}'):
                            try:
                                response_data = json.loads(json_str)
                                if 'delta' in response_data['choices'][0]:
                                    content = response_data['choices'][0]['delta'].get('content', '')
                                    # 实时格式化响应
                                    formatted_content = format_response(content)
                                    logger.info(f"接收数据:{formatted_content}")
                                    assistant_response += formatted_content
                                    updated_history = history[:-1] + [["assistant", assistant_response]]
                                    yield updated_history
                                if response_data.get('choices', [{}])[0].get('finish_reason') == "stop":
                                    logger.info(f"接收JSON数据结束")
                                    break
                            except json.JSONDecodeError as e:
                                logger.error(f"JSON解析错误: {e}")
                                yield history[:-1] + [["assistant", "解析响应时出错，请稍后再试。"]]
                                break
                        else:
                            logger.info(f"无效JSON格式: {json_str}")
                    else:
                        logger.info(f"收到空行")
                else:
                    logger.info("流式响应结束但未明确结束")
                    yield history[:-1] + [["assistant", "未收到完整响应。"]]
        except requests.RequestException as e:
            logger.error(f"请求失败: {e}")
            yield history[:-1] + [["assistant", "请求失败，请稍后再试。"]]

    # 非流式输出
    else:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_json = response.json()
        assistant_content = response_json['choices'][0]['message']['content']
        # 格式化响应
        formatted_content = format_response(assistant_content)
        logger.info(f"非流式输出，格式化后的内容是: {formatted_content}")
        updated_history = history[:-1] + [["assistant", formatted_content]]
        yield updated_history


# Gradio 前端界面
with gr.Blocks() as demo:
    chatbot = gr.Chatbot(label="聊天对话")

    with gr.Row():
        with gr.Column(scale=8):
            message = gr.Textbox(label="请输入消息", placeholder="在此输入您的消息")
        with gr.Column(scale=2):
            send = gr.Button("发送")

    # 发送按钮点击后，处理模型的响应
    send.click(send_message, [message, chatbot], chatbot)
    message.submit(send_message, [message, chatbot], chatbot)
    send.click(lambda: "", None, message)
    message.submit(lambda: "", None, message)


if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)


