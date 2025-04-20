# 1、RAG检索增强生成基础概念
## 1.1 RAG定义及技术方案架构
### （1）RAG定义
**RAG（Retrieval Augmented Generation，检索增强生成）** 是一种结合检索和生成能力的自然语言处理技术，通过外部知识检索增强大语言模型（LLM）的生成能力。

- **核心思想**：  
  类似于人类在回答问题时会查阅资料，RAG通过检索外部知识库（通常是向量数据库）为LLM提供上下文相关的信息，从而生成更准确、实时的回答。  
  RAG将生成模型的创造性与检索系统的精准性结合，弥补LLM知识的局限性。

- **主要目标**：  
  - **解决LLM知识的时效性问题**：LLM的训练数据有截止时间，无法涵盖最新信息，而RAG可以通过检索实时更新的知识库获取最新数据。  
  - **弥补领域知识的不足**：LLM可能缺乏特定行业或私有领域的专业知识，RAG通过检索企业内部文档或专业数据库提供定制化知识。  
  - **提升回答的准确性和可信度**：通过引用外部知识，减少生成内容中的“幻觉”问题。

- **场景类比**：  
  RAG类似于“开卷考试”：LLM在回答问题前，先通过检索系统“翻书”查找相关资料，再结合自身语言能力生成答案。  
  另一个类比是“智能助手”：用户提问时，助手快速查阅知识库（如企业文档、网页、数据库），然后基于查到的信息生成自然语言回答。

- **应用场景**：  
  - 智能客服：基于企业知识库回答用户问题。  
  - 学术研究：检索学术论文生成综述或回答专业问题。  
  - 实时问答：结合新闻或社交媒体数据回答时事问题。  
  - 企业内部搜索：基于内部文档生成复杂问题的解答。


### （2）技术方案架构
RAG的技术架构分为 **离线阶段** 和 **在线阶段**，通过模块化的流程实现检索与生成的协同工作。

#### 1. 离线阶段（数据准备与索引构建）
离线阶段的目标是将外部知识库处理为可检索的结构化数据，存入向量数据库。

1. **文档加载**：  
   - 从多种数据源（如PDF、Word、网页、数据库、API等）加载原始文档或数据。  
   - 支持的格式包括结构化数据（如表格、JSON）和非结构化数据（如文本、图像）。  
   - 补充：需考虑数据清洗，去除噪声（如格式标记、无关内容）以提升后续处理质量。

2. **文档切分**：  
   - 将长文档切分为较小的片段（chunks），以适应Embedding模型的输入长度限制（通常为几百到几千个字符）。  
   - 切分策略：  
     - 按段落、句子或固定长度切分。  
     - 语义切分：基于语义相似性（如使用NLP模型）确保切分后的片段语义完整。  
   - 补充：切分粒度需平衡上下文完整性与检索效率，过小的片段可能丢失语义，过大的片段可能降低检索精准度。

3. **向量化**：  
   - 使用Embedding模型（如BERT、Sentence-BERT、OpenAI的text-embedding-ada-002等）将文档片段转换为高维向量表示（通常为768维或更高）。  
   - Embedding模型的作用是将文本的语义信息映射到向量空间，相似语义的文本在向量空间中距离较近。  
   - 补充：  
     - 可选择多模态Embedding模型（如CLIP）处理图像、文本等多模态数据。  
     - Embedding模型需定期更新以适应语义变化或新领域需求。

4. **灌入向量数据库**：  
   - 将生成的向量及其对应的原始文本片段存储到向量数据库（如ChromDB、Milvus、Weaviate、Faiss、Pinecone等）。  
   - 向量数据库通过高效的索引结构（如HNSW、IVF）支持快速的最近邻搜索（ANN，Approximate Nearest Neighbor）。  
   - 补充：  
     - 可存储元数据（如文档来源、时间戳、权限）以支持更复杂的检索逻辑。  
     - 数据库需支持动态更新，以适应知识库内容的增删改。

#### 2. 在线阶段（实时查询与生成）
在线阶段的目标是基于用户问题检索相关知识并生成回答。

1. **获取用户问题**：  
   - 接收用户输入的自然语言问题或指令。  
   - 补充：可对问题进行预处理（如拼写校正、意图识别）以提高检索效果。

2. **用户问题向量化**：  
   - 使用与离线阶段相同的Embedding模型将用户问题转换为向量表示，确保查询向量与知识库向量在同一语义空间。  
   - 补充：可引入查询扩展（Query Expansion）技术，如同义词替换或语义改写，增强检索的召回率。

3. **检索向量数据库**：  
   - 在向量数据库中执行最近邻搜索，检索与问题向量最相似的文档片段（通常返回Top-K个结果）。  
   - 补充：  
     - 可结合传统关键字搜索（如BM25）与向量搜索，形成混合检索（Hybrid Search）以提升准确性。  
     - 检索结果可通过重排序模型（Reranker）进一步优化，基于语义相关性对Top-K结果重新排序。

4. **构造Prompt模版**：  
   - 将检索到的文档片段和用户问题填入预定义的Prompt模版，形成完整的输入。  
   - 示例Prompt模版：  
     ```
     根据以下信息回答问题：
     [检索到的文档片段1]
     [检索到的文档片段2]
     问题：[用户问题]
     回答：
     ```
   - 补充：Prompt设计需优化以引导LLM生成简洁、准确的回答，避免冗长或偏离主题。

5. **调用LLM生成回复**：  
   - 将构造好的Prompt输入到LLM，由LLM生成自然语言回答。  
   - 补充：可引入后处理步骤，如答案提取、格式化或引用标注，以提高回答的可读性和可信度。

6. **返回结果**：  
   - 将生成的回答返回给用户，同时可附带检索到的文档片段或来源链接以增强透明性。  
   - 补充：支持用户反馈机制（如点赞、纠错），用于优化检索和生成效果。

### （3）几个关键概念
以下是对关键概念的补充和细化，突出其在RAG中的作用及实际意义。

1. **向量数据库的意义**：  
   - **快速检索**：向量数据库通过高效的索引算法（如HNSW、IVF）实现毫秒级的语义搜索，满足实时应用的需求。  
   - **语义搜索**：相较于传统关键字匹配，向量数据库基于语义相似性检索，能捕捉同义表达或隐含语义。  
   - **扩展性**：支持大规模数据存储与查询，适合企业级知识库管理。  
   - 补充：向量数据库还支持多模态搜索（如文本+图像）和权限控制（如基于用户角色的访问限制）。

2. **向量生成与Embedding模型**：  
   - 向量数据库本身不生成向量，依赖Embedding模型将文本、图像等数据转换为向量表示。  
   - Embedding模型的选择直接影响检索质量：  
     - 通用模型（如OpenAI的Embedding模型）适合广泛场景。  
     - 领域定制模型（如针对医疗、法律的fine-tuned模型）在特定场景下效果更佳。  
   - 补充：Embedding模型需与LLM的语义空间对齐，避免检索与生成的不一致性。

3. **向量数据库与传统数据库的互补关系**：  
   - **向量数据库**：擅长语义搜索和非结构化数据处理，适合模糊匹配和语义相关性检索。  
   - **传统关系型数据库**：擅长结构化数据查询（如SQL）和精确匹配，适合数值、表格等数据管理。  
   - **实际应用中的结合**：  
     - 向量数据库用于初步语义检索，返回候选文档。  
     - 关系型数据库用于存储元数据、执行精确过滤或聚合查询。  
     - 示例：企业知识管理系统中，向量数据库检索文档内容，关系型数据库管理文档的权限和版本信息。  
   - 补充：混合架构（如通过API或中间件整合两者）是实际部署中的常见方案。

4. **补充概念**：  
   - **知识库更新**：RAG系统需支持知识库的动态更新（如增量索引、向量重算）以保持知识的时效性。  
   - **上下文长度限制**：LLM的输入长度限制（如4096 token）要求检索结果精炼，需通过Top-K选择或内容摘要技术优化。  
   - **评估指标**：RAG系统的效果可通过检索召回率（Recall）、生成准确性（BLEU、ROUGE）、用户满意度等指标评估。         

### （4）RAG的优势与挑战
为了更全面地理解RAG，以下补充其优势和潜在挑战。

#### 优势：
1. **知识扩展**：通过外部知识库，RAG突破了LLM的知识边界，支持实时和领域特定知识的引入。  
2. **减少幻觉**：检索到的真实文档作为上下文，降低LLM生成错误或虚构内容的风险。  
3. **灵活性**：可适配不同领域和数据源，易于扩展到多模态（如图像、视频）应用。  
4. **透明性**：可提供检索来源，增强用户对回答的可信度感知。

#### 挑战：
1. **检索质量依赖性**：如果检索结果不准确或不相关，生成的回答质量会显著下降。  
2. **计算成本**：向量化和LLM推理需要较高的计算资源，尤其在大规模知识库中。  
3. **知识库维护**：需要定期更新和清洗知识库以确保数据的时效性和准确性。  
4. **多语言支持**：在多语言场景下，Embedding模型和LLM需支持跨语言语义对齐。  
5. **隐私与安全**：处理私有数据时，需确保数据加密、访问控制和合规性。   

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
项目名称:RagLangChainV3Test                              
虚拟环境名称保持与项目名称一致                 

## 3.3 将相关代码拷贝到项目工程中           
直接将下载的代码文件夹拷贝到新建的项目目录下                                         
 
## 3.4 安装项目依赖           
命令行终端中直接运行如下命令安装依赖包                       
pip install langchain==0.3.23                        
pip install langchain-openai==0.3.12         
pip install langchain_community==0.3.21         
pip install langchain-chroma==0.2.3          
pip install chromadb==1.0.5                           
pip install fastapi==0.115.12                                   
pip install uvicorn==0.34.0           
pip install gradio==5.24.0                                      
pip install concurrent-log-handler==0.9.25                       
pip install pdfminer.six                   
pip install nltk==3.9.1             
pip install sentence-transformers==3.4.1                  
或运行如下命令安装          
pip install -r requirements.txt                


# 4、项目测试
## 4.1 案例：健康档案私有知识库搭建和检索
### （1）使用脚本测试大模型调用服务
进入01_RagDemoWithLangChain文件夹下，在使用python llmsTest.py命令启动脚本前，需根据自己的实际情况调整代码中的如下参数                     
utils/llms.py中关于大模型配置参数的调整，以及utils.config.py脚本中的服务IP、PORT、LLM_TYPE等设置               
### （2）文本预处理后进行灌库 
这里以pdf文件为例，在input文件夹下准备了两份pdf文件。健康档案.pdf:测试中文pdf文档处理，DeepSeek_R1.pdf:测试英文pdf文档处理                
在utils文件夹下提供了pdfSplitTest_Ch.py脚本工具用来处理中文文档、pdfSplitTest_En.py脚本工具用来处理英文文档                 
vectorSaveTest.py脚本执行调用tools中的工具进行文档预处理后进行向量计算及灌库                  
进入01_RagDemoWithLangChain文件夹下，在运行python vectorSaveTest.py命令启动脚本前，需根据自己的实际情况调整utils/config.py代码中的如下参数：               
选择使用哪种模型标志设置，LLM_TYPE = "openai"                       
设置待处理的文件内容文类型，中文或英文，TEXT_LANGUAGE = 'Chinese'                  
文件所在路径，INPUT_PDF = "input/健康档案.pdf"                     
指定文件中待处理的页码，全部页码则填None PAGE_NUMBERS = None                                      
chromaDB向量数据库的持久化存储文件夹路径CHROMADB_DIRECTORY = "chromaDB"                
待查询的chromaDB向量数据库的集合名称CHROMADB_COLLECTION_NAME = "demo001"                  
### （3-1）启动API接口服务 
进入01_RagDemoWithLangChain文件夹下，在使用python main.py命令启动脚本前，需根据自己的实际情况调整代码中的如下参数                                                    
utils/llms.py中关于大模型配置参数的调整，以及utils.config.py脚本中的服务IP、PORT、LLM_TYPE等设置                  
### （3-2）启动API接口服务(re-ranker)        
re-ranker是一种用于信息检索系统的技术，旨在对初步检索到的结果进行进一步排序，以提高相关性和准确性                    
通常在一个信息检索任务中，系统会首先根据查询条件从大量文档或数据中初步筛选出一组候选结果                  
然后通过一个re-ranker模型对这些候选结果进行细致的分析和重新排序，以确保最相关的结果排在最前面                    
首先通过该地址下载other文件夹，下载完成后将other压缩文件解压后拷贝到项目工程01_RagDemoWithLangChain下即可                   
链接: https://pan.baidu.com/s/1yJZjxwFHo3oH5jDBa1zSqg?pwd=n7ux 提取码: n7ux                 
进入01_RagDemoWithLangChain文件夹下，在使用python mainWithReranker.py命令启动脚本前，需根据自己的实际情况调整代码中的如下参数                                                    
utils/llms.py中关于大模型配置参数的调整，以及utils.config.py脚本中的服务IP、PORT、LLM_TYP、RERANK_MODELE等设置           
运行python mainWithReranker.py命令启动脚本前，需根据自己的实际情况调整代码中的如下参数：                                  
### （4）运行apiTest脚本进行接口调用测试              
进入01_RagDemoWithLangChain文件夹下，在使用python apiTest.py命令启动脚本前，需根据自己的实际情况调整代码中的如下参数，运行成功后，可以查看smith的跟踪情况                  
是否要流式输出可设置stream_flag = False或True，检查URL地址中的IP和PORT是否和main脚本中相同                 
### （5）运行webUI脚本进行测试             
进入01_RagDemoWithLangChain文件夹下，在使用python webUI.py命令启动脚本前，需根据自己的实际情况调整代码中的如下参数，运行成功后，可以查看smith的跟踪情况                  
是否要流式输出可设置stream_flag = False或True，检查URL地址中的IP和PORT是否和main脚本中相同            
**注意事项:**              
在测试使用调用oneapi(阿里通义千问)、阿里通义千问原生接口时，会报错如下所示：                 
openai.BadRequestError: Error code: 400 - {'error': {'message': 'input should not be none.: payload.input.contents (request id: 2024082015351785023974771558878)', 'type': 'upstream_error', 'param': '400', 'code': 'bad_response_status_code'}}              
经过分析后，langchain_openai/embeddings包中的base.py源码中默认如下代码的true改为false                 
check_embedding_ctx_length: bool = False                    
源码完整路径如下所示:                   
/opt/anaconda3/envs/RagLangchainTest/lib/python3.11/site-packages/langchain_openai/embeddings/base.py           
修改后重新启动main服务，进行重新测试               


