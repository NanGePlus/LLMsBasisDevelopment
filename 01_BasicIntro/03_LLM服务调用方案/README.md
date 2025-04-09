# LLM服务调用方案 
# 1、gpt大模型使用方案              
国内无法直接访问，可以使用代理的方式，具体代理方案自己选择                          
这里推荐大家使用:https://nangeai.top/register?aff=Vxlp                          

# 2、非gpt大模型方案 OneAPI方式或大模型厂商原生接口
## 2.1 OneAPI是什么
官方介绍：是OpenAI接口的管理、分发系统             
支持 Azure、Anthropic Claude、Google PaLM 2 & Gemini、智谱 ChatGLM、百度文心一言、讯飞星火认知、阿里通义千问、360 智脑以及腾讯混元               
## 2.2 安装、部署
使用官方提供的release软件包进行安装部署 ，详情参考如下链接中的手动部署：                  
https://github.com/songquanpeng/one-api                 
下载OneAPI可执行文件one-api并上传到服务器中然后，执行如下命令后台运行             
sudo chmod -R 777 one-api                   
nohup ./one-api --port 3000 --log-dir ./logs > output.log 2>&1 &            
ps aux | grep one-api              
运行成功后，浏览器打开如下地址进入one-api页面，默认账号密码为：root 123456                 
http://IP:3000/             
## 2.3 创建渠道和令牌 
创建渠道：大模型类型(通义千问)、APIKey(通义千问申请的真实有效的APIKey)                
创建令牌：创建OneAPI的APIKey，后续代码中直接调用此APIKey                  
阿里百炼大模型:https://bailian.console.aliyun.com/console?tab=model#/model-market                  

# 3、本地开源大模型方案 Ollama安装、启动、下载大模型          
### 3.1 Ollama是什么 
Ollama是一个轻量级、跨平台的工具和库，专门为本地大语言模型(LLM)的部署和运行提供支持            
它旨在简化在本地环境中运行大模型的过程，不需要依赖云服务或外部API，使用户能够更好地掌控和使用大型模型                  
### 3.2 Ollama安装、启动、下载大模型 
安装Ollama，进入官网 https://ollama.com 下载对应系统版本直接安装即可              
启动Ollama，安装所需要使用的本地模型，执行指令进行安装:                                                           
ollama pull deepseek-r1:14b                                                                   
执行执行运行大模型进行交互                
ollama run deepseek-r1:14b                










