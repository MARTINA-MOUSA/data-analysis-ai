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
        if 'auto_dashboard' not in st.session_state:
            st.session_state.auto_dashboard = None
        if 'report' not in st.session_state:
            st.session_state.report = None
        if 'color_theme' not in st.session_state:
            st.session_state.color_theme = 'default'
    
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
        st.dataframe(col_info_df, width='stretch')
        
        st.markdown("---")
        
        # Data preview
        st.subheader("Data Preview")
        st.dataframe(df.head(10), width='stretch')
        
        # Statistics
        st.subheader("Statistical Summary")
        st.dataframe(df.describe(), width='stretch')
    
    def render_auto_dashboard_tab(self):
        """Render auto-generated Power BI-like dashboard"""
        st.header("📊 Auto Dashboard")
        st.markdown("**AI-Generated Dashboard - No Code Required!**")
        
        if not st.session_state.data_handler.is_loaded():
            st.info("👆 Please upload a CSV file from the sidebar to get started")
            return
        
        if not st.session_state.agent:
            st.error("AI Agent not initialized")
            return
        
        # Color theme selector
        st.markdown("### 🎨 Choose Color Theme")
        theme_cols = st.columns(4)
        themes = ['default', 'blue', 'dark', 'corporate']
        theme_labels = ['Default', 'Blue', 'Dark', 'Corporate']
        
        for idx, (theme, label) in enumerate(zip(themes, theme_labels)):
            with theme_cols[idx]:
                if st.button(label, key=f"theme_{theme}", use_container_width=True):
                    st.session_state.color_theme = theme
                    st.rerun()
        
        if st.session_state.color_theme:
            st.info(f"Selected theme: **{st.session_state.color_theme.title()}**")
        
        st.markdown("---")
        
        # Generate dashboard button
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            generate_btn = st.button("🚀 Generate Dashboard", type="primary", use_container_width=True)
        with col2:
            if st.session_state.auto_dashboard:
                refresh_btn = st.button("🔄 Refresh", use_container_width=True)
            else:
                refresh_btn = False
        
        # Generate or refresh dashboard
        if generate_btn or (refresh_btn and st.session_state.auto_dashboard):
            with st.spinner("🤖 AI is analyzing your data and creating a Power BI-like dashboard..."):
                try:
                    dashboard_data = st.session_state.agent.generate_auto_dashboard(
                        color_theme=st.session_state.color_theme
                    )
                    if 'error' not in dashboard_data:
                        st.session_state.auto_dashboard = dashboard_data
                        st.success("✅ Dashboard generated successfully!")
                    else:
                        st.error(f"Error: {dashboard_data.get('error')}")
                except LLMError as e:
                    logger.error(f"LLM error: {e}")
                    st.error(f"AI service error: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error: {e}", exc_info=True)
                    st.error(f"Unexpected error: {str(e)}")
        
        # Display dashboard
        if st.session_state.auto_dashboard:
            dashboard = st.session_state.auto_dashboard
            
            # Show insights
            if dashboard.get('insights'):
                with st.expander("📊 Dashboard Insights", expanded=False):
                    for insight in dashboard['insights']:
                        st.markdown(f"• {insight}")
            
            st.markdown("---")
            
            # Display metrics
            if dashboard.get('visualizations'):
                metrics_viz = [v for v in dashboard['visualizations'] if v.get('type') == 'metrics']
                if metrics_viz:
                    st.subheader("📈 Key Metrics")
                    metrics = metrics_viz[0].get('data', [])
                    cols = st.columns(min(len(metrics), 6))
                    for idx, metric in enumerate(metrics[:6]):
                        with cols[idx % len(cols)]:
                            if metric.get('value') is not None:
                                st.metric(
                                    label=metric.get('label', metric['name']),
                                    value=metric.get('display_value', f"{metric['value']:,.0f}")
                                )
                    st.markdown("---")
                
                # Display visualizations in HR Analytics Dashboard layout (all in one page)
                plotly_viz = [v for v in dashboard['visualizations'] if v.get('type') == 'plotly_figure']
                table_viz = [v for v in dashboard['visualizations'] if v.get('type') == 'table']
                
                if plotly_viz or table_viz:
                    st.subheader("📊 Complete Dashboard - All Visualizations")
                    
                    # Separate charts by position
                    top_right = [v for v in plotly_viz if v.get('position') == 'top_right']
                    middle_left = [v for v in plotly_viz if v.get('position') == 'middle_left']
                    middle_center = [v for v in plotly_viz if v.get('position') == 'middle_center']
                    middle_right = [v for v in table_viz if v.get('position') == 'middle_right']
                    bottom_left = [v for v in plotly_viz if v.get('position') == 'bottom_left']
                    bottom_center = [v for v in plotly_viz if v.get('position') == 'bottom_center']
                    bottom_right = [v for v in plotly_viz if v.get('position') == 'bottom_right']
                    
                    # If no positions assigned, organize by type
                    if not any([top_right, middle_left, middle_center, middle_right, bottom_left, bottom_center, bottom_right]):
                        pie_charts = [v for v in plotly_viz if v.get('chart_type') == 'pie']
                        bar_charts = [v for v in plotly_viz if v.get('chart_type') == 'bar' or v.get('chart_type') == 'horizontal_bar']
                        area_charts = [v for v in plotly_viz if v.get('chart_type') == 'area']
                        
                        # Assign positions based on order
                        top_right = pie_charts[:1] if pie_charts else []
                        middle_left = [b for b in bar_charts if b.get('subtype') == 'horizontal'][:1] if bar_charts else []
                        middle_center = pie_charts[1:2] if len(pie_charts) > 1 else []
                        bottom_left = [b for b in bar_charts if b.get('subtype') == 'vertical'][:1] if bar_charts else []
                        bottom_center = area_charts[:1] if area_charts else []
                        bottom_right = [b for b in bar_charts if b.get('subtype') == 'horizontal'][1:2] if len([b for b in bar_charts if b.get('subtype') == 'horizontal']) > 1 else []
                    
                    # Top Row: Empty space on left, Donut chart on right
                    if top_right:
                        top_row_cols = st.columns([2, 1])
                        with top_row_cols[1]:
                            viz = top_right[0]
                            if viz.get('title'):
                                st.markdown(f"**{viz['title']}**")
                            if viz.get('description'):
                                st.caption(viz['description'])
                            chart_key = f"auto_top_right_{hash(viz.get('title', 'top_right'))}"
                            st.plotly_chart(viz['data'], use_container_width=True, height=350, key=chart_key)
                        st.markdown("---")
                    
                    # Middle Row: 3 columns (Horizontal Bar, Donut, Table)
                    if middle_left or middle_center or middle_right:
                        mid_cols = st.columns(3)
                        
                        # Middle Left - Horizontal Bar
                        if middle_left:
                            with mid_cols[0]:
                                viz = middle_left[0]
                                if viz.get('title'):
                                    st.markdown(f"**{viz['title']}**")
                                if viz.get('description'):
                                    st.caption(viz['description'])
                                chart_key = f"auto_mid_left_{hash(viz.get('title', 'mid_left'))}"
                                st.plotly_chart(viz['data'], use_container_width=True, height=400, key=chart_key)
                        
                        # Middle Center - Donut
                        if middle_center:
                            with mid_cols[1]:
                                viz = middle_center[0]
                                if viz.get('title'):
                                    st.markdown(f"**{viz['title']}**")
                                if viz.get('description'):
                                    st.caption(viz['description'])
                                chart_key = f"auto_mid_center_{hash(viz.get('title', 'mid_center'))}"
                                st.plotly_chart(viz['data'], use_container_width=True, height=400, key=chart_key)
                        
                        # Middle Right - Table
                        if middle_right:
                            with mid_cols[2]:
                                viz = middle_right[0]
                                if viz.get('title'):
                                    st.markdown(f"**{viz['title']}**")
                                if viz.get('description'):
                                    st.caption(viz['description'])
                                # Display table data
                                table_data = viz.get('data')
                                if table_data is not None:
                                    st.dataframe(table_data, width='stretch', height=400)
                        st.markdown("---")
                    
                    # Bottom Row: 3 columns (Vertical Bar, Area, Horizontal Bar)
                    if bottom_left or bottom_center or bottom_right:
                        bot_cols = st.columns(3)
                        
                        # Bottom Left - Vertical Bar
                        if bottom_left:
                            with bot_cols[0]:
                                viz = bottom_left[0]
                                if viz.get('title'):
                                    st.markdown(f"**{viz['title']}**")
                                if viz.get('description'):
                                    st.caption(viz['description'])
                                chart_key = f"auto_bot_left_{hash(viz.get('title', 'bot_left'))}"
                                st.plotly_chart(viz['data'], use_container_width=True, height=400, key=chart_key)
                        
                        # Bottom Center - Area Chart
                        if bottom_center:
                            with bot_cols[1]:
                                viz = bottom_center[0]
                                if viz.get('title'):
                                    st.markdown(f"**{viz['title']}**")
                                if viz.get('description'):
                                    st.caption(viz['description'])
                                chart_key = f"auto_bot_center_{hash(viz.get('title', 'bot_center'))}"
                                st.plotly_chart(viz['data'], use_container_width=True, height=400, key=chart_key)
                        
                        # Bottom Right - Horizontal Bar
                        if bottom_right:
                            with bot_cols[2]:
                                viz = bottom_right[0]
                                if viz.get('title'):
                                    st.markdown(f"**{viz['title']}**")
                                if viz.get('description'):
                                    st.caption(viz['description'])
                                chart_key = f"auto_bot_right_{hash(viz.get('title', 'bot_right'))}"
                                st.plotly_chart(viz['data'], use_container_width=True, height=400, key=chart_key)
                    
                    # Display any remaining visualizations
                    all_displayed = top_right + middle_left + middle_center + middle_right + bottom_left + bottom_center + bottom_right
                    remaining_viz = [v for v in plotly_viz if v not in all_displayed]
                    
                    if remaining_viz:
                        st.markdown("---")
                        st.markdown("#### 📋 Additional Visualizations")
                        for row in range(0, len(remaining_viz), 3):
                            rem_cols = st.columns(min(3, len(remaining_viz) - row))
                            for col_idx, col in enumerate(rem_cols):
                                viz_idx = row + col_idx
                                if viz_idx < len(remaining_viz):
                                    viz = remaining_viz[viz_idx]
                                    with col:
                                        if viz.get('title'):
                                            st.markdown(f"**{viz['title']}**")
                                        if viz.get('description'):
                                            st.caption(viz['description'])
                                        chart_key = f"auto_additional_{row}_{col_idx}_{viz_idx}_{hash(viz.get('title', f'{row}_{col_idx}'))}"
                                        st.plotly_chart(viz['data'], use_container_width=True, height=320, key=chart_key)
                else:
                    st.info("No visualizations generated yet. Click 'Generate Dashboard' to create visualizations.")
            else:
                st.info("No dashboard data available. Click 'Generate Dashboard' to create one.")
        else:
            st.info("""
            👆 **Click 'Generate Dashboard' to automatically create a Power BI-like dashboard!**
            
            The AI will:
            - Analyze your data structure
            - Generate appropriate visualizations
            - Create key metrics and KPIs
            - Provide insights automatically
            
            **No coding required!** 🚀
            """)
    
    def render_report_tab(self):
        """Render comprehensive data analysis report"""
        st.header("📄 Data Analysis Report")
        st.markdown("**Comprehensive Report with Predictions & Insights**")
        
        if not st.session_state.data_handler.is_loaded():
            st.info("👆 Please upload a CSV file from the sidebar to get started")
            return
        
        if not st.session_state.agent:
            st.error("AI Agent not initialized")
            return
        
        # Generate report button
        col1, col2 = st.columns([1, 4])
        with col1:
            generate_report_btn = st.button("📊 Generate Report", type="primary", use_container_width=True)
        
        # Generate report
        if generate_report_btn:
            with st.spinner("🤖 AI is generating comprehensive report with predictions and insights..."):
                try:
                    report_data = st.session_state.agent.generate_report()
                    if 'error' not in report_data:
                        st.session_state.report = report_data
                        st.success("✅ Report generated successfully!")
                    else:
                        st.error(f"Error: {report_data.get('error')}")
                except LLMError as e:
                    logger.error(f"LLM error: {e}")
                    st.error(f"AI service error: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error: {e}", exc_info=True)
                    st.error(f"Unexpected error: {str(e)}")
        
        # Display report
        if st.session_state.report:
            report = st.session_state.report
            
            # Data Overview
            st.markdown("## 📊 Data Overview")
            overview = report.get('data_overview', {})
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Rows", f"{overview.get('total_rows', 0):,}")
            with col2:
                st.metric("Total Columns", overview.get('total_columns', 0))
            with col3:
                st.metric("Null Values", f"{overview.get('null_values', 0):,}")
            with col4:
                st.metric("Duplicate Rows", f"{overview.get('duplicate_rows', 0):,}")
            
            st.markdown("---")
            
            # Data Explanation
            st.markdown("## 📖 What This Data Contains")
            explanation = report.get('data_explanation', '')
            st.markdown(explanation)
            
            st.markdown("---")
            
            # Data Quality
            st.markdown("## ✅ Data Quality Assessment")
            quality = report.get('data_quality', {})
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Completeness", f"{quality.get('completeness_percentage', 0):.1f}%")
            with col2:
                st.metric("Quality Score", f"{quality.get('quality_score', 0):.1f}/100")
            with col3:
                st.metric("Duplicate %", f"{quality.get('duplicate_percentage', 0):.1f}%")
            
            if quality.get('columns_with_nulls'):
                st.warning(f"⚠️ Columns with null values: {', '.join(quality['columns_with_nulls'][:5])}")
            
            st.markdown("---")
            
            # Predictions
            st.markdown("## 🔮 Predictions & Forecasts")
            predictions = report.get('predictions', '')
            st.markdown(predictions)
            
            st.markdown("---")
            
            # Key Insights
            st.markdown("## 💡 Key Insights")
            insights = report.get('insights', '')
            st.markdown(insights)
            
            st.markdown("---")
            
            # Recommendations
            st.markdown("## 🎯 Recommendations")
            recommendations = report.get('recommendations', '')
            st.markdown(recommendations)
            
            st.markdown("---")
            
            # Statistical Summary
            with st.expander("📈 Statistical Summary", expanded=False):
                stats = report.get('statistical_summary', {})
                if stats:
                    for col, values in list(stats.items())[:10]:
                        st.markdown(f"### {col}")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.write(f"**Mean:** {values.get('mean', 0):.2f}")
                            st.write(f"**Median:** {values.get('median', 0):.2f}")
                        with col2:
                            st.write(f"**Std:** {values.get('std', 0):.2f}")
                            st.write(f"**Min:** {values.get('min', 0):.2f}")
                        with col3:
                            st.write(f"**Max:** {values.get('max', 0):.2f}")
                            st.write(f"**Q25:** {values.get('q25', 0):.2f}")
                        with col4:
                            st.write(f"**Q75:** {values.get('q75', 0):.2f}")
                        st.markdown("---")
        else:
            st.info("""
            👆 **Click 'Generate Report' to create a comprehensive data analysis report!**
            
            The report will include:
            - 📖 Detailed explanation of what the data contains
            - ✅ Data quality assessment
            - 🔮 Predictions and forecasts
            - 💡 Key insights and findings
            - 🎯 Actionable recommendations
            - 📈 Statistical summary
            
            **All in Arabic!** 🚀
            """)
    
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
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary", "📊 Auto Dashboard", "📄 Report", "🤖 AI Insights"])

        with tab1:
            self.render_summary_tab()

        with tab2:
            self.render_auto_dashboard_tab()

        with tab3:
            self.render_report_tab()

        with tab4:
            self.render_ai_insights_tab()

