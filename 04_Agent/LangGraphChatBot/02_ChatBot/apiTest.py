import requests
import json
import logging


# Author:@南哥AGI研习社 (B站 or YouTube 搜索“南哥AGI研习社”)


# 设置日志模版
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


url = "http://localhost:8012/v1/chat/completions"
headers = {"Content-Type": "application/json"}


# 默认非流式输出 True or False
stream_flag = False


input_text = "记住你的名字是南哥。"
# input_text = "200元以下，流量大的套餐有啥？"
# input_text = "你叫什么名字？"
# input_text = "就刚刚提到的这个套餐，是多少钱？"
# input_text = "有没有豪华套餐？"
# input_text = "你叫什么名字？"


# input_text = "你的名字是南哥。"
# input_text = "200元以下，流量大的套餐有啥？"
# input_text = "你叫什么名字？"
# input_text = "就刚刚提到的这个套餐，是多少钱？"
# input_text = "有没有豪华套餐？"
# input_text = "你叫什么名字？"


# 封装请求的参数
data = {
    "messages": [{"role": "user", "content": input_text}],
    "stream": stream_flag,
    "userId":"123456",
    "conversationId":"123456"
}


# 接收流式输出处理
if stream_flag:
    full_response = ""
    try:
        with requests.post(url, stream=True, headers=headers, data=json.dumps(data)) as response:
            for line in response.iter_lines():
                if line:
                    json_str = line.decode('utf-8').strip("data: ")
                    # 检查是否为空或不合法的字符串
                    if not json_str:
                        logger.info(f"收到空字符串，跳过...")
                        continue
                    # 确保字符串是有效的JSON格式
                    if json_str.startswith('{') and json_str.endswith('}'):
                        try:
                            data = json.loads(json_str)
                            if 'delta' in data['choices'][0]:
                                delta_content = data['choices'][0]['delta'].get('content', '')
                                full_response += delta_content
                                logger.info(f"流式输出，响应部分是: {delta_content}")
                            if data['choices'][0].get('finish_reason') == "stop":
                                logger.info(f"接收JSON数据结束")
                                logger.info(f"完整响应是: {full_response}")
                        except json.JSONDecodeError as e:
                            logger.info(f"JSON解析错误: {e}")
                    else:
                        logger.info(f"无效JSON格式: {json_str}")
    except Exception as e:
        logger.error(f"Error occurred: {e}")

# 接收非流式输出处理
else:
    # 发送post请求
    response = requests.post(url, headers=headers, data=json.dumps(data))
    # logger.info(f"接收到返回的响应原始内容: {response.json()}\n")
    content = response.json()['choices'][0]['message']['content']
    logger.info(f"非流式输出，响应内容是: {content}\n")