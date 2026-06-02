SALES_ANALYSIS_PROMPT = """
你是一名电商数据分析专家。请分析以下销售数据并提供业务洞察：

数据摘要：
{data_summary}

请简洁回答：
1. 销售趋势
2. 表现最好/最差的类别
3. 关键发现

用3-5句话总结，不要超过200字。
"""

ANOMALY_DETECTION_PROMPT = """
你是一名异常检测专家。请分析以下数据并识别潜在异常：

数据：
{data}

请列出异常项及其严重程度（高/中/低），每项不超过一句话。
"""

REPORT_GENERATION_PROMPT = """
你是一名专业的报告生成员。请根据以下数据分析结果生成一份简洁的业务报告内容片段（不要生成完整HTML页面）：

分析结果：
{analysis_result}

报告要求：
- 只输出HTML内容片段，不要包含<html>、<head>、<body>等标签
- 执行摘要：放入 class="section-card executive" 的div中
- 关键指标：用表格展示，放入 class="section-card metrics" 的div中
- 关键发现：放入 class="section-card findings" 的div中，使用ul列表
- 建议行动项：放入 class="section-card actions" 的div中，使用ul列表
- 每个section-card内部要有 class="section-title" 的div，包含图标和标题
- 保持简洁，总长度不超过500字

示例格式：
<div class="section-card executive">
    <div class="section-title">
        <span class="icon">📋</span>
        <h3>执行摘要</h3>
    </div>
    <p>...</p>
</div>

<div class="section-card metrics">
    <div class="section-title">
        <span class="icon">📊</span>
        <h3>关键指标</h3>
    </div>
    <table>
        <tr><th>指标</th><th>数值</th></tr>
        <tr><td>总销售额</td><td>¥XX,XXX</td></tr>
    </table>
</div>

<div class="section-card findings">
    <div class="section-title">
        <span class="icon">💡</span>
        <h3>关键发现</h3>
    </div>
    <ul>
        <li>发现1...</li>
    </ul>
</div>

<div class="section-card actions">
    <div class="section-title">
        <span class="icon">📌</span>
        <h3>建议行动项</h3>
    </div>
    <ul>
        <li>建议1...</li>
    </ul>
</div>
"""

ALERT_SUMMARIZATION_PROMPT = """
请将以下警报信息汇总成一份清晰的摘要：

警报列表：
{alerts}

请按严重程度排序，用简洁的语言描述。
"""

CHART_DESCRIPTION_PROMPT = """
根据以下数据，请描述应该使用什么类型的图表来展示，并说明理由：

数据类型：{data_type}
数据摘要：{data_summary}

请推荐最合适的图表类型并简要解释原因。
"""