"""
LangChain Agent for Data Analysis
"""
# Import AgentExecutor - handle different LangChain versions
import importlib
from typing import Dict, List, Optional

# Try multiple import strategies
AgentExecutor = None
create_openai_tools_agent = None

# Strategy 1: Standard import
try:
    from langchain.agents import AgentExecutor, create_openai_tools_agent
except ImportError:
    pass

# Strategy 2: Try importing separately
if AgentExecutor is None:
    try:
        from langchain.agents import AgentExecutor
    except ImportError:
        pass

if create_openai_tools_agent is None:
    try:
        from langchain.agents import create_openai_tools_agent
    except ImportError:
        pass

# Strategy 3: Try from agent_executor module
if AgentExecutor is None:
    try:
        from langchain.agents.agent_executor import AgentExecutor
    except (ImportError, AttributeError):
        pass

# Strategy 4: Try from langchain_core
if AgentExecutor is None:
    try:
        from langchain_core.agents import AgentExecutor
    except ImportError:
        pass

# Strategy 5: Dynamic import using importlib
if AgentExecutor is None or create_openai_tools_agent is None:
    try:
        agents_module = importlib.import_module('langchain.agents')
        if AgentExecutor is None:
            AgentExecutor = getattr(agents_module, 'AgentExecutor', None)
        if create_openai_tools_agent is None:
            create_openai_tools_agent = getattr(agents_module, 'create_openai_tools_agent', None)
    except Exception:
        pass

# Final check - if still None, provide helpful error
if AgentExecutor is None:
    raise ImportError(
        "Could not import AgentExecutor from langchain.agents. "
        "Please install/upgrade LangChain: pip install --upgrade langchain langchain-openai langchain-core"
    )

if create_openai_tools_agent is None:
    raise ImportError(
        "Could not import create_openai_tools_agent from langchain.agents. "
        "Please install/upgrade LangChain: pip install --upgrade langchain langchain-openai"
    )

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.data_analysis_tools import ColumnInfoTool, GenerateCodeTool
from ai.feature_advisor import FeatureEngineeringAdvisor
from ai.llm_client import BasetenLLMClient
from back.data_handler import DataHandler
from config import Config


class DataAnalysisAgent:
    """LangChain agent for data analysis tasks"""
    
    def __init__(self, data_handler: DataHandler):
        """
        Initialize the agent
        
        Args:
            data_handler: DataHandler instance with loaded data
        """
        self.data_handler = data_handler
        self.llm_client = BasetenLLMClient()
        self.feature_advisor: Optional[FeatureEngineeringAdvisor] = None
        
        # Create custom LLM wrapper for LangChain
        # Note: LangChain's ChatOpenAI uses base_url parameter for custom endpoints
        self.llm = ChatOpenAI(
            model=Config.BASETEN_MODEL,
            api_key=Config.BASETEN_API_KEY,
            base_url=Config.BASETEN_BASE_URL,
            temperature=0.7,
            max_tokens=2000
        )
        
        # Initialize tools
        self.tools = self._create_tools()
        
        # Create agent
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _create_tools(self):
        """Create list of tools for the agent"""
        column_tool = ColumnInfoTool(self.data_handler)
        code_tool = GenerateCodeTool(self.data_handler, self.llm_client)
        
        # Return BaseTool instances directly for tools API
        return [column_tool, code_tool]
    
    def _create_agent(self):
        """Create the LangChain agent"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful data analysis assistant. 
            You have access to tools that can help you analyze data.
            When asked a question about data:
            1. First, use get_column_info to understand the data structure
            2. Then, use generate_analysis_code to create code for the analysis
            3. Provide clear explanations of what you're doing.
            
            Always be helpful and provide insights about the data.
            
            📊 Key Principles for Data Analysis:
            
            1️⃣ Start with the question before the data - Correct analysis starts from understanding the problem, not just exploring data.
            
            2️⃣ Understand the business context well - Numbers without context have no meaning. Always consider the business implications.
            
            3️⃣ Focus on data cleaning - This is the foundation of any successful analysis. Check for missing values, duplicates, and data quality issues.
            
            4️⃣ Clarify insights simply - The decision is more important than technical details. Present findings in a clear, actionable way.
            
            5️⃣ Continuously develop skills - Use appropriate tools (SQL, Power BI, Excel, Python) effectively for the task at hand.
            
            Remember: The goal is not to display numbers... The goal is to help the business make the right decision. 🚀"""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return agent
    
    def analyze(self, query: str) -> str:
        """
        Analyze data based on user query
        
        Args:
            query: User's question or analysis request
            
        Returns:
            str: Analysis result or code
        """
        try:
            result = self.agent_executor.invoke({"input": query})
            return result.get("output", "Analysis completed")
        except Exception as e:
            return f"Error during analysis: {str(e)}"
    
    def auto_analyze(self) -> dict:
        """
        Perform automatic analysis of the dataset
        
        Returns:
            dict: Dictionary with summary, insights, and suggested visualizations
        """
        if not self.data_handler.is_loaded():
            return {
                "error": "No data loaded"
            }
        
        info = self.data_handler.get_info()
        
        # Generate automatic analysis
        auto_query = f"""
        Perform a comprehensive automatic analysis of this dataset:
        - Columns: {', '.join(info.get('columns', []))}
        - Shape: {info.get('shape', 'unknown')}
        
        Follow these data analysis principles:
        1️⃣ Start with the question - Understand what business problem this data might solve
        2️⃣ Understand business context - Provide insights that matter to decision-makers
        3️⃣ Focus on data cleaning - Assess data quality, missing values, duplicates
        4️⃣ Clarify insights simply - Present findings in a clear, actionable way
        5️⃣ Use appropriate analysis methods - Choose the right techniques for the data
        
        Provide:
        1. Summary statistics
        2. Key insights with business context
        3. Suggested visualizations
        4. Data quality assessment
        5. Actionable recommendations
        
        Remember: The goal is to help the business make the right decision, not just display numbers.
        """
        
        analysis_result = self.analyze(auto_query)
        
        return {
            "summary": analysis_result,
            "columns": info.get("columns", []),
            "shape": info.get("shape")
        }
    
    def generate_auto_dashboard(self, color_theme: str = 'default') -> dict:
        """
        Generate an automatic Power BI-like dashboard
        
        Args:
            color_theme: Color theme name ('default', 'blue', 'dark', 'corporate')
        
        Returns:
            dict: Dashboard with visualizations
        """
        from ai.dashboard_generator import AutoDashboardGenerator
        from back.analysis_engine import AnalysisEngine
        
        if not self.data_handler.is_loaded():
            return {"error": "No data loaded"}
        
        analysis_engine = AnalysisEngine(self.data_handler.get_dataframe())
        generator = AutoDashboardGenerator(
            self.data_handler,
            analysis_engine,
            self.llm_client,
            color_theme=color_theme
        )
        
        return generator.generate_dashboard()
    
    def generate_report(self) -> dict:
        """
        Generate comprehensive data analysis report
        
        Returns:
            dict: Complete report with explanations, predictions, and insights
        """
        from ai.report_generator import ReportGenerator
        
        if not self.data_handler.is_loaded():
            return {"error": "No data loaded"}
        
        generator = ReportGenerator(self.data_handler, self.llm_client)
        return generator.generate_comprehensive_report()

    def generate_feature_suggestions(
        self,
        dataset_info: Dict[str, Any],
        outlier_summary: Optional[List[Dict[str, Any]]] = None,
        erd_summary: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate feature engineering recommendations."""
        if self.feature_advisor is None:
            self.feature_advisor = FeatureEngineeringAdvisor(self.llm_client)

        return self.feature_advisor.generate_suggestions(
            dataset_info=dataset_info,
            outlier_summary=outlier_summary,
            erd_summary=erd_summary,
        )

