# 电商后台自动报表与异常预警系统

## 项目简介

基于 Agent 技术的企业级电商数据分析平台，实现智能报表生成、异常检测与预警功能，帮助企业快速洞察业务数据，及时发现运营异常。

## 方向

方向二：企业级应用软件的 Agent 改造

## 技术栈

- **AI IDE**: Trae CN
- **LLM**: DeepSeek API (DeepSeek-v4-pro)
- **框架**: LangGraph、LangChain
- **Web框架**: FastAPI
- **数据库**: SQLite + SQLAlchemy
- **可视化**: Chart.js
- **模板引擎**: Jinja2

## 目录结构

```
src/
├── app/
│   ├── agent/          # Agent 业务组件
│   │   ├── sales_analyzer.py      # 销售数据分析 Agent
│   │   ├── anomaly_detector.py    # 异常检测 Agent
│   │   ├── report_generator.py    # 报表生成 Agent
│   │   ├── visualization_agent.py # 数据可视化 Agent
│   │   └── chat_agent.py          # 智能问答 Agent
│   ├── api/            # REST API 路由
│   │   └── routes.py   # API 端点定义
│   ├── workflow/       # LangGraph 工作流
│   │   └── workflow.py # 报表生成工作流
│   ├── llm/            # LLM 客户端
│   │   ├── client.py   # DeepSeek API 客户端
│   │   └── prompts.py  # 提示词模板
│   ├── models/         # 数据库模型
│   │   └── database.py # SQLAlchemy ORM 定义
│   ├── services/       # 业务服务层
│   │   └── user_service.py # 用户认证服务
│   ├── templates/      # 前端模板
│   │   ├── index.html      # 登录页面
│   │   ├── dashboard.html  # 数据仪表盘
│   │   ├── reports.html    # 智能报表页面
│   │   └── alerts.html     # 异常预警页面
│   ├── config.py       # 配置管理
│   └── main.py         # FastAPI 主入口
└── main.py             # 项目启动入口
```

## 环境搭建

### 1. 依赖安装

```bash
pip install -r requirements.txt
```

### 2. 环境变量配置

创建 `.env` 文件，填入您的 DeepSeek API Key：

```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DATABASE_URL=sqlite:///./ecommerce.db
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. 启动步骤

```bash
python src/main.py
```

访问地址：`http://localhost:8000`

## 项目状态

- [x] Proposal
- [x] MVP
- [ ] Final

## 功能特性

### 销售数据分析
- 多维度销售趋势分析
- 商品分类销售占比统计
- 关键业务指标计算

### 异常检测预警
- 销售额异常波动检测
- 库存不足预警
- 智能告警分级管理

### 智能报表生成
- 日报/周报自动生成
- LLM 驱动的自然语言报告
- 数据可视化图表

### 智能问答
- 报表内容问答
- 常见问题快速回答
- 响应速度优化（缓存机制）

## 登录账号

| 用户名 | 密码 |
|--------|------|
| admin | 123456 |
| zhangsan | 123456 |
| lisi | 123456 |