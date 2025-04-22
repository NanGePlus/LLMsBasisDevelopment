# 1、基础概念
## 1.1  KAG框架
**(1)KAG是什么**               
检索增强生成（RAG）技术推动了领域应用与大模型结合。然而，RAG 存在着向量相似度与知识推理相关性差距大、对知识逻辑（如数值、时间关系、专家规则等）不敏感等问题，这些缺陷阻碍了专业知识服务的落地             
2024年10月24日，OpenSPG 发布 v0.5 版本，正式发布了知识增强生成（KAG）的专业领域知识服务框架                 
官方网址:https://openspg.yuque.com/r/organizations/homepage                     
Github地址:https://github.com/OpenSPG/KAG                                   
**(2)KAGV0.7版本更新**                     
https://github.com/OpenSPG/KAG/releases/tag/v0.7                             


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
项目名称:KAGV7Test                              
虚拟环境名称保持与项目名称一致                 

## 3.3 将相关代码拷贝到项目工程中            
直接将下载的代码文件夹拷贝到新建的项目目录下                                         


# 4、功能测试 
## 4.1 OpenSPG-Server服务部署和启动                                   
首先，下载官方提供的最新版本的OpenSPG-Server的docker-compose.yml文件                 
链接:https://github.com/OpenSPG/openspg/blob/master/dev/release/docker-compose.yml                        
然后，进入到配置文件所在目录使用docker部署和启动OpenSPG-Server，运行的指令为:                     
docker compose -f docker-compose.yml up -d                       
对于docker的安装，这里以Mac系统为例，windows无本质差别，根据自己的操作系统选择下载安装包 官网链接 https://www.docker.com/ ，直接安装即可               
安装完成后，找到Docker图标双击运行，Docker服务启动成功                                  
启动成功后，对应的服务查看方式如下:                          
**neo4j:** 浏览器输入 http://127.0.0.1:7474/browser/ , 访问neo4j图数据库，默认用户名和密码:neo4j  neo4j@openspg                                                          
**Minio:** 浏览器输入 http://127.0.0.1:9000 , 访问Minio存储，默认用户名和密码:minio  minio@openspg                 
**mysql:** 打开mysql客户端软件，远程访问数据库，默认用户名和密码:root  openspg               

## 4.2 产品模式测试
### (1) 访问WEB端                 
浏览器输入 http://127.0.0.1:8887, 可访问openspg-kag产品模式的WEB端，默认用户名和密码:openspg openspg@kag            
首次登录会要求修改密码                   
### (2) 全局配置
注意进行拷贝填写的的时候前后不能出现空格                
**图存储配置参数**                    
database:kag                                                          
password:neo4j@openspg                                     
uri:neo4j://release-openspg-neo4j:7687                                           
user:neo4j                                  
**向量配置参数**                            
type:openai                                  
model:text-embedding-3-small                                                                       
base_url:https://nangeai.top/v1                                                        
api_key:sk-qqzZO0rjALbvkRXGwNNJp7q3lEtFja03zRx2H0iU6r3Sb2aq                                                                      
**提示词中英文配置参数**                          
biz_scene:default                                      
language:zh                                
**模型配置参数**                                                            
代理方式 国内外大模型           
base_url = "https://nangeai.top/v1"               
api_key = "sk-KSu01Dw71ZJfQGquoFTSxcMTUWzUUnVJ0de6Jf4vjnvzFMYw"                
model = "o3-mini-all"           
embedding_model = "text-embedding-3-small"           
OneAPI方式 国内外大模型(阿里通义千问为例)                   
base_url = "http://139.224.72.218:3000/v1"             
api_key = "sk-joQuR8CibdPQ33vR2fFaDfE7B1B24cA0AeF7F3881200946f"              
model = "qwen-plus"           
embedding_model = "text-embedding-v1"              
大模型厂商原生接口 阿里通义千问为例               
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"                
api_key = "sk-74e71713b8844da2a5d905835377c842"                
model = "qwen-plus"                
embedding_model = "text-embedding-v1"                       
### (3) 按照如下流程测试
创建知识库-编辑知识模型-创建任务-构建知识库、查看日志、抽取结果知识图谱-知识探查-知识库配置权限配置-推理问答            
(1)创建知识库          
设置知识库中文名称和英文名称(JayChouTest)，其他配置保持默认               
(2)调整知识模型              
进入到知识库构建页面，在知识模型中，根据自己的实际业务需求编辑知识模模型，这里以JayChouTest.schema为例              
(3)创建任务               
进入到知识库构建页面，创建任务，任务选择从本地文件上传文件JayChou.txt,然后选择使用的Chat模型，最后进行创建等待完成             
任务构建整体BuilderChain流程如下: Reader->Splitter->Extractor->Vectorizer->Alignment-Writer               
(4)查看详情       
查看知识库的基本配置、执行日志、抽取效果、抽取知识模型等           
(5)知识探查       
按照知识类型、知识名称进行探查，支持列表和画布两种方式          
(6)推理问答          
支持普通问答和深度推理                           

## 4.3 开发者模式测试             
### (1) 安装依赖
下载KAG源码 https://github.com/OpenSPG/KAG 解压后将源码工程拷贝到项目根目录，截止2025-04-22,最新版本是v0.7.0                          
新建命令行终端，按照如下指令进行依赖安装               
cd KAG                          
pip install -e .                    
安装完成之后可以运行如下指令验证是否安装成功                               
knext --version                        
### (2)调整配置文件                                                          
将根目录下的config目录下的example_config.yaml文件拷贝一份到根目录,根据自己的业务修改配置参数             
KAG支持txt、pdf、markdown、docx、json、csv、语雀等，根据自己要处理的文本类型进行相关设置                 
### (3)使用配置文件初始化项目                                   
新建命令行终端，运行如下命令进行项目创建和初始化                                     
knext project create --config_path ./example_config.yaml             
若项目创建完成，修改了配置文件，需要运行如下命令进行更新                  
knext project update --proj_path .                  
### (3)提交schema
项目初始化完成后，进入到对应的项目文件夹下，根据实际业务需求调整schema，调整完成后再执行提交schema                
knext schema commit                     
### (4)构建索引                                   
首先将文档拷贝到新建项目文件夹中的builder/data下，支持txt、pdf、markdown、docx、json、csv等                          
并可以根据自身业务需求，在builder/prompt目录下新增:ner.py、std.py、triple.py                 
**注意:** 代码中是通过注解的方式配置到配置文件中                      
打开命令行终端，进入脚本所在目录cd builder，运行 python indexer.py 命令                   
构建脚本启动后，会在当前工作目录下生成任务的 checkpoint 目录，记录了构建链路的 checkpoint 和统计信息            
KAG 框架基于 checkpoint 文件提供了断点续跑的功能。如果由于程序出错或其他外部原因（如 LLM 余额不足）导致任务中断，可以重新执行 indexer.py，KAG 会自动加载 checkpoint 文件并复用已有结果                         
索引构建成功后，可登录到 http://127.0.0.1:8887/或 http://127.0.0.1:7474/browser/ 查看知识图谱                 
### (5)检索                              
打开命令行终端，进入脚本所在目录solver，运行 python query.py 命令                              
根据自身业务需求，可设置相关prompt内容:如resp_generator.py                          
也可以在产品端进行测试 http://127.0.0.1:8887/                

