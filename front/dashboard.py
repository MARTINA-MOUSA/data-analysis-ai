"""
Streamlit Dashboard Components
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Optional, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from back.data_handler import DataHandler
from back.analysis_engine import AnalysisEngine
from back.exceptions import DataLoadError, AnalysisExecutionError, LLMError
from back.logger import logger
from ai.agent import DataAnalysisAgent


class Dashboard:
    """Main dashboard class for Streamlit UI"""
    
    def __init__(self):
        """Initialize dashboard"""
        if 'data_handler' not in st.session_state:
            st.session_state.data_handler = DataHandler()
        if 'analysis_engine' not in st.session_state:
            st.session_state.analysis_engine = None
        if 'agent' not in st.session_state:
            st.session_state.agent = None
        if 'visualizations' not in st.session_state:
            st.session_state.visualizations = []
        if 'insights' not in st.session_state:
            st.session_state.insights = []
    
    def render_sidebar(self):
        """Render sidebar with file upload"""
        st.sidebar.title("📊 Data Analysis AI")
        st.sidebar.markdown("---")
        
        uploaded_file = st.sidebar.file_uploader(
            "Upload CSV File",
            type=['csv'],
            help="Upload a CSV file to analyze"
        )
        
        if uploaded_file is not None:
            try:
                if st.session_state.data_handler.load_from_bytes(
                    uploaded_file.read(),
                    uploaded_file.name
                ):
                    st.session_state.data_handler.df = st.session_state.data_handler.get_dataframe()
                    st.session_state.analysis_engine = AnalysisEngine(
                        st.session_state.data_handler.df
                    )
                    st.session_state.agent = DataAnalysisAgent(
                        st.session_state.data_handler
                    )
                    st.sidebar.success("✅ File loaded successfully!")
                    
                    # Show data info
                    info = st.session_state.data_handler.get_info()
                    st.sidebar.markdown("### Data Info")
                    st.sidebar.write(f"**Shape:** {info['shape'][0]} rows × {info['shape'][1]} columns")
                    st.sidebar.write(f"**Columns:** {len(info['columns'])}")
            except DataLoadError as e:
                logger.error(f"Data load error: {e}")
                st.sidebar.error(f"❌ Error loading file: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                st.sidebar.error(f"❌ Unexpected error: {str(e)}")
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Navigation")
        st.sidebar.markdown("Use the tabs above to navigate between different views")
    
    def render_summary_tab(self):
        """Render summary tab"""
        st.header("📋 Summary")
        
        if not st.session_state.data_handler.is_loaded():
            st.info("👆 Please upload a CSV file from the sidebar to get started")
            return
        
        df = st.session_state.data_handler.get_dataframe()
        info = st.session_state.data_handler.get_info()
        
        # Basic statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Rows", info['shape'][0])
        with col2:
            st.metric("Total Columns", info['shape'][1])
        with col3:
            st.metric("Memory Usage", f"{info['memory_usage'] / 1024:.2f} KB")
        with col4:
            null_total = sum(info['null_counts'].values())
            st.metric("Null Values", null_total)
        
        st.markdown("---")
        
        # Column information
        st.subheader("Column Information")
        col_info_df = pd.DataFrame({
            'Column': info['columns'],
            'Data Type': [str(info['dtypes'][col]) for col in info['columns']],
            'Null Count': [info['null_counts'][col] for col in info['columns']]
        })
        st.dataframe(col_info_df, use_container_width=True)
        
        st.markdown("---")
        
        # Data preview
        st.subheader("Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Statistics
        st.subheader("Statistical Summary")
        st.dataframe(df.describe(), use_container_width=True)
    
    def render_visualizations_tab(self):
        """Render visualizations tab"""
        st.header("📈 Visualizations")
        
        if not st.session_state.data_handler.is_loaded():
            st.info("👆 Please upload a CSV file from the sidebar to get started")
            return
        
        if not st.session_state.analysis_engine:
            st.error("Analysis engine not initialized")
            return
        
        # Show saved visualizations
        if st.session_state.visualizations:
            st.subheader("Generated Visualizations")
            for idx, viz in enumerate(st.session_state.visualizations):
                with st.expander(f"Visualization {idx + 1}", expanded=True):
                    if viz['type'] == 'plotly_figure':
                        st.plotly_chart(viz['data'], use_container_width=True)
                    st.code(viz['code'], language='python')
        
        st.markdown("---")
        
        # Manual code execution
        st.subheader("Create Custom Visualization")
        code_input = st.text_area(
            "Enter Python code (use 'df' for dataframe, 'px' or 'go' for plotly):",
            height=200,
            help="Write Python code to create visualizations or perform analysis"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            execute_btn = st.button("▶️ Execute Code", type="primary")
        
        if execute_btn and code_input:
            with st.spinner("Executing code..."):
                try:
                    result, output, error = st.session_state.analysis_engine.execute_code(code_input)
                    
                    if error:
                        st.error(f"Error: {error}")
                        st.code(output, language='python')
                    else:
                        if result is not None:
                            formatted = st.session_state.analysis_engine.format_result(result)
                            
                            if formatted['type'] == 'plotly_figure':
                                st.plotly_chart(formatted['data'], use_container_width=True)
                                # Save visualization
                                st.session_state.visualizations.append({
                                    'type': 'plotly_figure',
                                    'data': formatted['data'],
                                    'code': code_input
                                })
                            elif formatted['type'] == 'dataframe':
                                st.dataframe(formatted['data'], use_container_width=True)
                            elif formatted['type'] == 'series':
                                st.dataframe(formatted['data'], use_container_width=True)
                            else:
                                st.write("Result:", formatted['data'])
                    
                        if output:
                            st.text("Output:")
                            st.code(output)
                except AnalysisExecutionError as e:
                    logger.error(f"Analysis execution error: {e}")
                    st.error(f"Execution error: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error: {e}", exc_info=True)
                    st.error(f"Unexpected error: {str(e)}")
    
    def render_ai_insights_tab(self):
        """Render AI insights tab"""
        st.header("🤖 AI Insights")
        
        if not st.session_state.data_handler.is_loaded():
            st.info("👆 Please upload a CSV file from the sidebar to get started")
            return
        
        if not st.session_state.agent:
            st.error("AI Agent not initialized")
            return
        
        # Query input
        st.subheader("Ask a Question")
        user_query = st.text_input(
            "Enter your question about the data:",
            placeholder="e.g., What are the top 5 values in column X?",
            help="Ask any question about your data"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            ask_btn = st.button("🔍 Ask AI", type="primary")
        
        # Auto analysis button
        st.markdown("---")
        col1, col2 = st.columns([1, 4])
        with col1:
            auto_btn = st.button("✨ Auto Analyze", type="secondary")
        
        # Display results
        if ask_btn and user_query:
            with st.spinner("AI is analyzing..."):
                try:
                    response = st.session_state.agent.analyze(user_query)
                    st.session_state.insights.append({
                        'query': user_query,
                        'response': response
                    })
                except LLMError as e:
                    logger.error(f"LLM error: {e}")
                    st.error(f"AI service error: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error: {e}", exc_info=True)
                    st.error(f"Unexpected error: {str(e)}")
        
        if auto_btn:
            with st.spinner("Performing automatic analysis..."):
                try:
                    auto_result = st.session_state.agent.auto_analyze()
                    if 'error' not in auto_result:
                        st.session_state.insights.append({
                            'query': 'Auto Analysis',
                            'response': auto_result.get('summary', 'Analysis completed')
                        })
                except LLMError as e:
                    logger.error(f"LLM error: {e}")
                    st.error(f"AI service error: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error: {e}", exc_info=True)
                    st.error(f"Unexpected error: {str(e)}")
        
        # Show insights history
        if st.session_state.insights:
            st.markdown("---")
            st.subheader("Insights History")
            for idx, insight in enumerate(reversed(st.session_state.insights[-10:])):  # Show last 10
                with st.expander(f"💡 {insight['query']}", expanded=(idx == 0)):
                    st.markdown(insight['response'])
    
    def render(self):
        """Render the main dashboard"""
        st.set_page_config(
            page_title="Data Analysis AI",
            page_icon="📊",
            layout="wide"
        )
        
        self.render_sidebar()
        
        # Main tabs
        tab1, tab2, tab3 = st.tabs(["📋 Summary", "📈 Visualizations", "🤖 AI Insights"])
        
        with tab1:
            self.render_summary_tab()
        
        with tab2:
            self.render_visualizations_tab()
        
        with tab3:
            self.render_ai_insights_tab()

