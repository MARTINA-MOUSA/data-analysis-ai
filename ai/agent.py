"""
LangChain Agent for Data Analysis
"""
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from typing import List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.data_analysis_tools import ColumnInfoTool, GenerateCodeTool
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
    
    def _create_tools(self) -> List[Tool]:
        """Create list of tools for the agent"""
        column_tool = ColumnInfoTool(self.data_handler)
        code_tool = GenerateCodeTool(self.data_handler, self.llm_client)
        
        return [
            Tool(
                name=column_tool.name,
                func=column_tool._run,
                description=column_tool.description
            ),
            Tool(
                name=code_tool.name,
                func=lambda task, columns=None: code_tool._run(task, columns),
                description=code_tool.description
            )
        ]
    
    def _create_agent(self):
        """Create the LangChain agent"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful data analysis assistant. 
            You have access to tools that can help you analyze data.
            When asked a question about data:
            1. First, use get_column_info to understand the data structure
            2. Then, use generate_analysis_code to create code for the analysis
            3. Provide clear explanations of what you're doing.
            
            Always be helpful and provide insights about the data."""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(
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
        
        Provide:
        1. Summary statistics
        2. Key insights
        3. Suggested visualizations
        4. Data quality assessment
        """
        
        analysis_result = self.analyze(auto_query)
        
        return {
            "summary": analysis_result,
            "columns": info.get("columns", []),
            "shape": info.get("shape")
        }

