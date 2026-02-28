---
name: deploy-app
description: 在部署代码、用户提及部署（deploy）、发布（release）、环境（staging/production）等相关话题时使用此角色。
---


# 部署应用

使用提供的脚本部署应用程序。

## 使用方法

运行部署脚本：`scripts/deploy.sh <environment>`

其中 `<environment>` 可以是以下之一：
- `staging`（预发布/测试环境）
- `production`（生产环境）

示例：
```bash
scripts/deploy.sh staging
scripts/deploy.sh production
```

## 部署前验证

在执行部署之前，请先运行验证脚本：

```bash
python scripts/validate.py
```
