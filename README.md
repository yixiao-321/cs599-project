# 电商后台自动报表与异常预警系统

基于 Agent 技术的企业级电商数据分析平台，实现智能报表生成、异常检测与预警功能。

## 项目架构

```
cs599-project/
├── app/                          # 主应用目录
│   ├── __init__.py               # 应用初始化
│   ├── main.py                   # FastAPI 主入口
│   ├── config.py                 # 配置管理
│   ├── api/                      # REST API 路由
│   │   └── routes.py             # API 端点定义
│   ├── agent/                    # Agent 组件
│   │   ├── __init__.py
│   │   ├── sales_analyzer.py     # 销售数据分析 Agent
│   │   ├── anomaly_detector.py   # 异常检测 Agent
│   │   ├── report_generator.py   # 报表生成 Agent
│   │   └── visualization_agent.py # 数据可视化 Agent
│   ├── workflow/                 # LangGraph 工作流
│   │   └── workflow.py           # 报表生成工作流
│   ├── llm/                      # LLM 客户端
│   │   ├── client.py             # DeepSeek API 客户端
│   │   └── prompts.py            # 提示词模板
│   ├── models/                   # 数据库模型
│   │   └── database.py           # SQLAlchemy 模型定义
│   ├── data/                     # 数据处理
│   │   └── init_data.py          # 初始化示例数据
│   └── templates/                # 前端模板
│       ├── index.html            # 登录页面
│       ├── dashboard.html        # 数据仪表盘
│       ├── reports.html          # 智能报表页面
│       └── alerts.html           # 异常预警页面
├── .env                          # 环境变量配置
├── requirements.txt              # Python 依赖
└── main.py                       # 项目启动入口
```

## 技术栈

| 分类 | 技术 | 版本 |
|------|------|------|
| 语言 | Python | 3.11+ |
| 框架 | FastAPI | 0.110+ |
| Agent框架 | LangChain | 0.1+ |
| Agent框架 | LangGraph | 0.0.34+ |
| LLM | DeepSeek | v4-pro |
| 数据库 | SQLite | 内置 |
| 可视化 | Chart.js | 3.x |
| 模板引擎 | Jinja2 | 3.x |

## 功能特性

### 1. 销售数据分析
- 多维度销售趋势分析
- 商品分类销售占比统计
- 客户购买行为分析
- 关键业务指标计算

### 2. 异常检测预警
- 销售额异常波动检测
- 库存不足预警
- 客户行为异常识别
- 智能告警分级管理

### 3. 智能报表生成
- 日报自动生成
- 周报汇总分析
- LLM 驱动的自然语言报告
- 数据可视化图表

### 4. 可视化仪表盘
- 实时数据展示
- 交互式图表
- 告警状态监控
- 业务指标卡片

## 快速开始

### 环境要求

- Python 3.11+
- DeepSeek API Key

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd cs599-project
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**

编辑 `.env` 文件，填入您的 DeepSeek API Key：
```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DATABASE_URL=sqlite:///./ecommerce.db
API_HOST=0.0.0.0
API_PORT=8000
```

4. **启动应用**
```bash
python main.py
```

5. **访问应用**

打开浏览器访问：`http://localhost:8000`

## API 接口

### 销售分析
- `GET /api/sales/analysis?days=7` - 获取销售分析报告

### 异常检测
- `GET /api/anomalies/detect` - 检测异常并生成报告

### 报表生成
- `GET /api/reports/daily` - 获取日报
- `GET /api/reports/weekly` - 获取周报

### 告警管理
- `GET /api/alerts` - 获取告警列表
- `POST /api/alerts/{id}/resolve` - 处理告警

### 数据可视化
- `GET /api/visualizations/sales-trend` - 销售趋势图
- `GET /api/visualizations/category-sales` - 分类销售图
- `GET /api/visualizations/inventory` - 库存状态图

### 工作流
- `GET /api/workflow/run?days=7` - 执行完整报表生成工作流

## Agent 工作流

项目使用 LangGraph 构建报表生成工作流：

```
开始 → 销售分析 → 异常检测 → 生成可视化 → 生成报告 → 结束
```

### 工作流节点说明

1. **销售分析节点**：调用 SalesAnalyzer 分析销售数据
2. **异常检测节点**：调用 AnomalyDetector 检测异常
3. **可视化节点**：生成图表数据
4. **报告生成节点**：整合所有数据生成最终报告

## 数据库模型

### SalesRecord (销售记录)
- order_id: 订单ID
- product_name: 商品名称
- category: 分类
- quantity: 数量
- unit_price: 单价
- total_amount: 总价
- customer_id: 客户ID
- sale_date: 销售日期

### InventoryRecord (库存记录)
- product_id: 商品ID
- product_name: 商品名称
- category: 分类
- stock_quantity: 库存数量
- threshold: 预警阈值

### AlertRecord (告警记录)
- alert_type: 告警类型
- message: 告警消息
- severity: 严重程度 (high/medium/low)
- resolved: 是否已处理

## 开发说明

### 目录结构规范
- `app/api/`：REST API 路由定义
- `app/agent/`：Agent 业务逻辑组件
- `app/workflow/`：LangGraph 工作流定义
- `app/llm/`：LLM 客户端与提示词管理
- `app/models/`：数据库 ORM 模型
- `app/templates/`：前端 HTML 模板

### 代码规范
- 使用 PEP 8 代码风格
- 类型注解强制要求
- 模块化设计
- 异常处理完善

## 许可证

MIT License

## 参考文献

1. LangChain Documentation: https://python.langchain.com/
2. LangGraph Documentation: https://langchain-ai.github.io/langgraph/
3. DeepSeek API: https://platform.deepseek.com/
4. FastAPI Documentation: https://fastapi.tiangolo.com/