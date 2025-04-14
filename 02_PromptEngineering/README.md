# 1、Prompt工程基础概念
## 1.1 prompt基础
### (1) prompt定义
prompt就是你发给大模型的指令，比如编写个故事、讲个笑话、写份报告等                                                    
**貌似简单，但意义非凡**                             
(1)prompt是AGI时代的编程语言                                                                 
(2)prompt工程是AGI时代的软件工程                         
(3)prompt工程师是AGI时代的程序员                            
学会prompt工程，就像学用鼠标、键盘一样，是AGI时代的基本技能                                 
prompt工程门槛低，天花板高，所以有人戏称prompt为咒语                   
### (2) prompt调优
找到好的prompt是个持续迭代的过程，需要不断调优                 
如果知道训练数据是怎样的，参考训练数据来构造prompt是最好的                                
(1)把AI当人来看:你知道ta爱读西游记，就和ta聊西游记                                 
(2)不知道训练数据怎么办？看Ta是否主动告诉你。例如OpenAI的GPT对Markdown格式友好                        
(3)还有一种方式就是不断尝试。有时一字之差，对token生成概率的影响都可能是很大的，也可能毫无影响           
**试是常用方法，确实有运气因素，所以门槛低、天花板高**                        
**高质量prompt核心要点：指令具体、信息丰富、尽量少歧义**                           
### (3) prompt的典型构成
不要固守模版。模版的价值是提醒我们别漏掉什么，而不是必须遵守模版才行             
**角色:** 给AI定义一个最匹配任务的角色，比如:你是一位python编程大师                            
**指示:** 对任务进行描述               
**上下文:** 给出与任务相关的其它背景信息（尤其在多轮交互中）             
**例子:** 必要时给出举例，学术中称为one-shot learning, few-shot learning或in-context learning；实践证明其对输出正确性有很大帮助           
**输入:** 任务的输入信息；在提示词中明确的标识出输入                  
**输出:** 输出的格式描述，以便后继模块自动解析模型的输出结果，比如（JSON、XML）        
大模型对prompt开头和结尾的内容更敏感，先定义角色，其实就是在开头把问题域收窄，减少二义性                                                    

## 1.2 LangChain开发框架
### （1）LangChain定义 
LangChain 是一个开源框架，旨在帮助开发者利用大型语言模型（LLM）构建智能应用程序                    
它通过提供模块化的工具和组件，使得开发者能够轻松集成外部数据、上下文记忆和工具调用，从而增强LLM的能力                                 
截至2025年4月，LangChain的最新版本为V0.3。该框架支持Python和JavaScript两种主要编程语言，官方文档地址为：https://python.langchain.com/docs/introduction/                                           
### （2）LCEL定义
LCEL（LangChain Expression Language，LangChain 表达式语言）是LangChain框架中的一种声明式语言，最初被称为"chain"，用于简化和灵活地组合LLM的调用流程            
它通过定义一系列操作步骤（称为链，chain），将输入处理、模型调用和输出生成整合为一个可配置的管道。LCEL的主要特点包括:              
支持流式输出:允许实时处理和输出结果，适用于需要低延迟的场景                      
**异步支持:** 提供异步执行能力，提升大规模任务的效率               
**优化的并行执行:** 支持多个任务同时运行，减少等待时间               
**重试和回退:** 内置错误处理机制，确保链的鲁棒性               
**访问中间结果:** 开发者可以在链的任意阶段获取中间输出，便于调试和优化              
**输入和输出模式:** 支持定义严格的输入输出格式，确保一致性                 
**无缝LangSmith跟踪集成:** 与LangSmith平台紧密结合，便于监控和评估                    
**无缝LangServe部署集成:** 支持将链部署为REST API，简化生产环境集成                               
LCEL的设计目标是让开发者能够以声明式的方式快速构建复杂的LLM工作流，同时保持高度的可定制性和可扩展性                       
### （3）LangSmith               
LangChain不仅仅是一个独立的框架，它还与一系列相关工具（如 LangSmith、LangServe 和 LangGraph）共同构成了一个完整的开发生态系统                       
这些工具相互协作，覆盖了从开发、调试到部署的整个生命周期，进一步提升了基于大型语言模型（LLM）的应用程序构建效率                    
LangSmith是一个专为生产级LLM应用程序设计的平台，旨在帮助开发者监控、调试和优化基于LangChain的应用，官方文档地址为：https://docs.smith.langchain.com/                 
LangSmith的主要功能包括:                
**应用监控:** 实时跟踪 LLM 的输入、输出和性能指标              
**评估工具:** 提供测试和基准工具，帮助开发者评估模型的准确性和可靠性                    
**调试支持:** 记录中间步骤和日志，便于定位问题                 
**版本管理:** 支持对模型和链的版本控制，便于迭代开发             
**协作功能:** 允许多人团队共同管理和优化应用                 
LangSmith与LangChain和LCEL无缝集成，是构建健壮、可扩展LLM应用的重要工具，尤其适用于需要上线部署和持续优化的场景                

## 1.3 Gradio      
Gradio 是一个开源的 Python 库，旨在简化大模型应用程序的部署和演示。它提供了一个用户友好的界面，使开发者能够快速构建和分享交互式应用                        
官网地址:https://www.gradio.app/                      
以下是 Gradio 的一些主要特点:                                
**简单易用:** Gradio 的 API 设计非常直观，用户可以用几行代码创建应用，无需前端开发经验             
**支持多种输入输出:** Gradio 支持多种类型的输入（文本、图像、音频、视频等）和输出，方便用户与模型交互               
**实时预览:** 用户可以实时查看模型的输出，方便调试和展示              
**分享和部署:** 生成的应用可以通过链接共享，甚至可以在本地服务器上运行，使团队合作和用户反馈变得更加简单              
**集成友好:** Gradio 可以与多种机器学习框架（如 TensorFlow、PyTorch、Scikit-Learn 等）轻松集成，支持将已有模型快速转换为交互式应用             
**自定义界面:** 用户可以通过 Gradio 的组件自定义界面，调整布局和样式，以满足特定需求            
通过 Gradio，开发者能够快速展示他们的大模型应用，收集用户反馈，从而更好地优化和改进模型                      


# 2、前期准备工作
## 2.1 集成开发环境搭建  
anaconda提供python虚拟环境,pycharm提供集成开发环境                                              
**具体参考如下视频:**                        
【大模型应用开发-入门系列】03 集成开发环境搭建-开发前准备工作                         
https://youtu.be/KyfGduq5d7w                     
https://www.bilibili.com/video/BV1nvdpYCE33/                      

## 2.2 大模型LLM服务接口调用方案
(1)gpt大模型等国外大模型使用方案                  
国内无法直接访问，可以使用代理的方式，具体代理方案自己选择                        
这里推荐大家使用:https://nangeai.top/register?aff=Vxlp                        
(2)非gpt大模型方案 OneAPI方式或大模型厂商原生接口                                              
(3)本地开源大模型方案(Ollama方式)                                              
**具体参考如下视频:**                                           
【大模型应用开发-入门系列】04 大模型LLM服务接口调用方案                    
https://youtu.be/mTrgVllUl7Y               
https://www.bilibili.com/video/BV1BvduYKE75/                     
                

# 3、项目初始化
## 3.1 下载源码
GitHub或Gitee中下载工程文件到本地，下载地址如下：               
https://github.com/NanGePlus/LLMsBasisDevelopment                 
https://gitee.com/NanGePlus/LLMsBasisDevelopment                  

## 3.2 构建项目
使用pycharm构建一个项目，为项目配置虚拟python环境,python版本选择3.11                        
项目名称:LangChainV3Test                              
虚拟环境名称保持与项目名称一致                 

## 3.3 将相关代码拷贝到项目工程中           
直接将下载的代码文件夹拷贝到新建的项目目录下                                         
 
## 3.4 安装项目依赖           
命令行终端中直接运行如下命令安装依赖包                       
pip install langchain==0.3.23                        
pip install langchain-openai==0.3.12                                       
pip install fastapi==0.115.12                                   
pip install uvicorn==0.34.0                               
pip install langchain_community==0.3.21                                     
pip install gradio==5.24.0                                    
pip install concurrent-log-handler==0.9.25                      
或运行如下命令安装          
pip install -r requirements.txt                


# 4、项目测试
## 4.1 案例1:流量包推荐智能客服 
LangChain+FastAPI,将应用封装成API接口并进行调用，支持流式输出和非流式输出，并在前端处理流式和非流式数据，并使用Gradio完成WebUI页面的搭建，并完成整个前后端的交互                                
支持多种类型大模型国外大模型、国产大模型(如阿里通义千问等)、Ollama本地开源大模型(deepseek-r1)                            
历史对话记忆功能，使用V2版本中的RunnableWithMessageHistory(官方不会废除该功能)抽象进行实现               
#### （1）使用脚本测试大模型调用服务
进入BasicDemoWithLangChain文件夹下，在使用python llmsTest.py命令启动脚本前，需根据自己的实际情况调整代码中的如下参数                     
utils/llms.py中关于大模型配置参数的调整，以及utils.config.py脚本中的服务IP、PORT、LLM_TYPE等设置                 
#### （2）启动API接口服务 
进入BasicDemoWithLangChain文件夹下，在使用python main.py命令启动脚本前，需根据自己的实际情况调整代码中的如下参数                                                    
utils/llms.py中关于大模型配置参数的调整，以及utils.config.py脚本中的服务IP、PORT、LLM_TYPE等设置                 
### （3）运行apiTest脚本进行接口调用测试              
进入BasicDemoWithLangChain文件夹下，在使用python apiTest.py命令启动脚本前，需根据自己的实际情况调整代码中的如下参数，运行成功后，可以查看smith的跟踪情况                  
是否要流式输出可设置stream_flag = False或True，检查URL地址中的IP和PORT是否和main脚本中相同                 
#### （4）运行webUI脚本进行测试             
进入BasicDemoWithLangChain文件夹下，在使用python webUI.py命令启动脚本前，需根据自己的实际情况调整代码中的如下参数，运行成功后，可以查看smith的跟踪情况                  
是否要流式输出可设置stream_flag = False或True，检查URL地址中的IP和PORT是否和main脚本中相同            
 
