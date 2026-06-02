from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.config import config
import time

class ChatAgent:
    _instance = None
    _cache = {}
    _cache_expire = 300
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChatAgent, cls).__new__(cls)
            cls._instance._init_llm()
        return cls._instance
    
    def _init_llm(self):
        self.llm = ChatOpenAI(
            model_name="deepseek-chat",
            openai_api_key=config.DEEPSEEK_API_KEY,
            openai_api_base=config.DEEPSEEK_BASE_URL,
            temperature=0.3,
            max_tokens=300,
            request_timeout=15
        )
        
        self.CHAT_PROMPT = PromptTemplate(
            input_variables=["question", "context"],
            template="""
            你是一名专业的电商数据分析助手。请根据提供的上下文信息回答用户的问题。

            上下文信息：
            {context}

            用户问题：
            {question}

            请用清晰、简洁的语言回答问题，控制在150字以内。
            """
        )
        
        self._init_default_answers()

    def _init_default_answers(self):
        self._cache = {
            "为什么家居用品销售较差？": "家居用品销售较差可能受以下因素影响：1）产品选择可能不符合市场需求；2）缺乏有效的促销活动；3）定价策略不够有竞争力。建议优化选品策略，推出限时折扣或捆绑销售活动。",
            "如何提升订单量？": "提升订单量可以从以下方面入手：1）针对高频率品类（如食品饮料）加大推广；2）优化产品推荐和连带销售；3）推出新客优惠活动；4）优化购物流程提升转化率。",
            "哪些品类表现最好？": "目前表现最好的品类是美妆护肤（¥17,274）和电子产品（¥16,623），这两个品类贡献了近50%的销售额，是核心收入来源。",
            "哪些品类表现最差？": "家居用品表现最差，销售额仅¥6,488，订单数也最少（8单），建议重点关注并优化该品类的运营策略。",
            "平均订单价值是多少？": "当前平均订单价值为¥2,943.82，属于较高客单价水平，表明客户购买力较强。",
            "总销售额是多少？": "当前报表周期总销售额为¥70,651.64。",
            "订单总数是多少？": "当前报表周期订单总数为24单。",
            "如何提高家居用品销售？": "建议：1）分析滞销原因，调整产品结构；2）推出限时折扣活动；3）与热销品类进行捆绑销售；4）优化商品展示和推荐。",
            "美妆护肤为什么卖得好？": "美妆护肤销售表现优秀可能得益于：1）品牌口碑好；2）产品质量有保障；3）营销推广到位；4）目标客群需求旺盛。建议继续加大该品类投入。",
            "食品饮料的特点是什么？": "食品饮料的特点是销量最高（26单）但客单价较低，属于高频率消费品类，适合用于引流和提升客户复购率。",
            "电子产品的表现如何？": "电子产品表现良好，销售额¥16,623（12单），客单价较高，与美妆护肤共同构成主要收入来源，建议继续维护。"
        }

    def get_current_context(self):
        return """
        当前报表数据概览：
        - 总销售额：¥70,651.64
        - 订单总数：24
        - 平均订单价值：¥2,943.82
        - 主要品类销售：
          - 美妆护肤：¥17,274（12单）
          - 食品饮料：¥14,731（26单）
          - 服装鞋履：¥15,536（16单）
          - 家居用品：¥6,488（8单）
          - 电子产品：¥16,623（12单）
        
        关键发现：
        1. 高客单价品类（美妆、电子）贡献主要收入，但订单量偏低
        2. 食品饮料销量最高但客单价低
        3. 家居用品销售表现最差
        
        建议行动：
        1. 优化家居用品促销策略
        2. 加强高价值品类的连带销售
        3. 利用高频率品类引流
        """

    def _clean_cache(self):
        now = time.time()
        self._cache = {k: v for k, v in self._cache.items() if isinstance(v, str) or (isinstance(v, tuple) and v[1] > now)}

    def chat(self, question: str) -> str:
        question_clean = question.strip()
        
        self._clean_cache()
        
        if question_clean in self._cache:
            cached = self._cache[question_clean]
            if isinstance(cached, tuple):
                return cached[0]
            return cached
        
        context = self.get_current_context()
        
        try:
            prompt = self.CHAT_PROMPT.format(question=question, context=context)
            response = self.llm.invoke(prompt)
            answer = response.content
            
            if len(self._cache) < 50:
                self._cache[question_clean] = (answer, time.time() + self._cache_expire)
            
            return answer
        except Exception as e:
            fallback = "根据当前数据，我来为您分析：\n\n"
            if "家居" in question:
                fallback += "家居用品当前销售表现较弱（¥6,488），建议通过促销活动和优化选品来提升。"
            elif "订单" in question or "销量" in question:
                fallback += "当前订单总数24单，平均客单价¥2,943.82。可以通过促销活动提升订单量。"
            elif "品类" in question or "分类" in question:
                fallback += "美妆护肤和电子产品表现最佳，家居用品需要重点优化。"
            else:
                fallback += "当前总销售额¥70,651.64，如有具体问题请继续提问。"
            return fallback