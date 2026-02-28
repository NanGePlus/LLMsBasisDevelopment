# 集成开发环境搭建指南

在 Python 开发领域，Anaconda 和 Cursor 是两款非常流行的工具。它们各有特色，能为不同的开发需求提供强大支持。以下将简要介绍二者的安装和基础配置方法，帮助你快速搭建优质的开发环境。

---

## 1. Anaconda

Anaconda 是专为数据科学、机器学习和科学计算打造的开源 Python 与 R 发行版。只需访问官网  
<https://www.anaconda.com/>  
下载并根据操作系统选择合适的安装包进行安装即可。

Anaconda 的核心优势在于集成了 Conda 包管理和环境管理工具，使得一键安装常用库（如 NumPy、Pandas、Matplotlib 等）和创建独立虚拟环境变得极为便捷，有效避免了项目间的依赖冲突。

**主要组件包括：**
- **Conda**：高效的包和环境管理工具，轻松实现包的安装、更新与管理。
- **Anaconda Navigator**：可视化图形界面，适合不熟悉命令行的用户进行库与环境的管理。
- **预装丰富库**：安装后内置众多主流科学计算和数据分析库，无需手动配置。

---

## 2. Cursor

Cursor 是专为提升开发生产力而设计的一款 AI 编程工具。本质上是 VS Code 的深度分支，但无论是底层架构还是交互方式都围绕“让 AI 深度参与编程全流程”进行了优化，而不仅仅是增加一个侧边栏聊天框。

### 2.1 下载与安装

前往 Cursor 官网：  
<https://cursor.com/home>  
选择适合你操作系统的安装包下载安装。

### 2.2 基础配置

1. **安装 Python 插件**  
   快捷键 `Command+Shift+X` 打开扩展面板，搜索并安装 `ms-python` 插件。

2. **安装 Tokyo Night 主题**  
   同样在扩展面板搜索 `Tokyo Night` 并安装主题。

3. **安装 cursor 指令**  
   快捷键 `Command+Shift+P` 打开命令面板，输入并选择 `shell command: Install "cursor" command`。

### 2.3 创建项目

Cursor 的核心理念是“以文件夹为项目”，推荐如下步骤：

1. 打开命令行终端
2. 创建项目文件夹：`mkdir cursor_test`
3. 进入文件夹：`cd cursor_test`
4. 启动 Cursor 并打开当前项目：`cursor .`

### 2.4 项目初始化配置

- **配置 Python 解释器**  
  快捷键 `Command+Shift+P`，搜索 `python:select Interpreter`，选择 conda，指定已创建的虚拟环境或新建环境。

- **自定义命令（command）**  
  在项目根目录新建 `.cursor/commands` 文件夹，内放 Markdown 文件。可在对话框中通过 “/命令名” 启用。

- **自定义技能（skill）**  
  在 `.cursor/skills` 文件夹中创建技能，包含 `SKILL.md`、scripts（脚本）、references（文档）和 assets（静态资源），通过对话框 “/技能名” 启用。

- **自定义规则（rule）**  
  在 `.cursor/rules` 文件夹新建 Markdown 文件，用于设置开发规范或 AI 辅助行为。

- **自定义子代理（subAgent）**  
  在 `.cursor/agents` 文件夹添加 Markdown 文件，通过 “/子Agent名” 启用。目前内置有 explore（代码分析）、Bash（运行 shell）、Browser（浏览网页）三个子 Agent。

### 2.5 常用功能与用法

- **Tab 智能补全**：补全建议会以半透明幽灵文本展示，Tab 接受，ESC 拒绝。
- **Inline Edit 行内智能编辑**：选中内容后，按 `Command+K` 唤起对话框编辑。
- **Semantic Search 语义搜索**：支持智能代码/文本搜索。
- **MCP 服务**：可在 Settings → Tools/MCP 配置外部系统联动。
- **Chat AI 对话模式**：支持与 AI 交流、提问、头脑风暴、代码解释及调试。用“@”引用文件/文件夹，用“/”引用命令与技能。

---

更多资源与精选链接：
- [Cursor 插件与资源合集](https://cursor.directory/)
- [社区优秀 Cursor Rules 收录](https://github.com/PatrickJS/awesome-cursorrules)
