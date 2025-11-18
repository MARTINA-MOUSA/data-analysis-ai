"""
Data Analysis Tools - LangChain tools for data analysis
"""
from langchain.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel, Field
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from back.data_handler import DataHandler


class ColumnInfoInput(BaseModel):
    """Input schema for column info tool"""
    pass


class ColumnInfoTool(BaseTool):
    """Tool to get information about dataframe columns"""
    
    name = "get_column_info"
    description = "Get information about the columns in the dataframe. Use this to understand what data is available."
    args_schema: Type[BaseModel] = ColumnInfoInput
    
    def __init__(self, data_handler: DataHandler):
        super().__init__()
        self.data_handler = data_handler
    
    def _run(self) -> str:
        """Execute the tool"""
        if not self.data_handler.is_loaded():
            return "No data loaded. Please upload a CSV file first."
        
        info = self.data_handler.get_info()
        columns = info.get("columns", [])
        dtypes = info.get("dtypes", {})
        null_counts = info.get("null_counts", {})
        
        result = f"DataFrame has {len(columns)} columns:\n"
        for col in columns:
            dtype = str(dtypes.get(col, "unknown"))
            nulls = null_counts.get(col, 0)
            result += f"- {col}: {dtype} ({nulls} null values)\n"
        
        result += f"\nShape: {info.get('shape', 'unknown')} rows x columns"
        return result


class GenerateCodeInput(BaseModel):
    """Input schema for code generation tool"""
    task: str = Field(description="The analysis task or question to generate code for")
    columns: Optional[list] = Field(default=None, description="Specific columns to use (optional)")


class GenerateCodeTool(BaseTool):
    """Tool to generate Python/pandas/plotly code for data analysis"""
    
    name = "generate_analysis_code"
    description = """Generate Python code using pandas and plotly to analyze data. 
    The code should use 'df' as the dataframe variable.
    For visualizations, use plotly (px or go) and assign to 'fig' or 'result'.
    For calculations, assign results to 'result' variable.
    Always import necessary libraries at the start."""
    args_schema: Type[BaseModel] = GenerateCodeInput
    
    def __init__(self, data_handler: DataHandler, llm_client):
        super().__init__()
        self.data_handler = data_handler
        self.llm_client = llm_client
    
    def _run(self, task: str, columns: Optional[list] = None) -> str:
        """Execute the tool"""
        if not self.data_handler.is_loaded():
            return "No data loaded. Please upload a CSV file first."
        
        info = self.data_handler.get_info()
        column_names = info.get("columns", [])
        dtypes = info.get("dtypes", {})
        
        # Build context for LLM
        context = f"""
You are a data analysis expert. Generate Python code to accomplish the following task:

Task: {task}

Available columns:
{', '.join(column_names)}

Column types:
{', '.join([f"{col}: {dtype}" for col, dtype in dtypes.items()])}

Requirements:
1. Use pandas (pd) for data manipulation
2. Use plotly (px or go) for visualizations
3. The dataframe is already loaded as 'df'
4. For visualizations, create a plotly figure and assign it to 'fig' or 'result'
5. For calculations, assign the result to 'result' variable
6. Only output the Python code, no explanations
7. Import necessary libraries at the start

Generate the code:
"""
        
        messages = [
            {"role": "system", "content": "You are a Python data analysis expert. Generate clean, efficient code."},
            {"role": "user", "content": context}
        ]
        
        code = self.llm_client.get_full_response(
            messages=messages,
            max_tokens=2000,
            temperature=0.3
        )
        
        # Clean up code (remove markdown code blocks if present)
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()
        
        return code

