# Data Analysis AI 📊

AI-powered data analysis project using Streamlit, LangChain, and Baseten API

## Features

- 📁 Upload and automatically analyze CSV files
- 🤖 AI-powered data analysis and question answering
- 📈 Create interactive visualizations using Plotly
- 🔍 Automatic data analysis
- 💻 Execute Python code directly for custom analysis

## Project Structure

```
data-analysis-ai/
├── ai/                 # AI modules
│   ├── agent.py       # LangChain Agent
│   ├── llm_client.py  # Baseten API client
│   └── data_analysis_tools.py  # Analysis tools
├── front/             # User interface
│   └── dashboard.py   # Streamlit components
├── back/              # Business logic
│   ├── data_handler.py      # Data handler
│   └── analysis_engine.py   # Analysis engine
├── config.py          # Configuration
├── app.py             # Main entry point
├── .env               # Environment variables
└── requirements.txt   # Required libraries
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Setup `.env` file:
   - Copy `env.example` to `.env`
   - Or create `.env` manually and add:
```env
BASETEN_API_KEY=your_api_key_here
BASETEN_BASE_URL=https://inference.baseten.co/v1
BASETEN_MODEL=openai/gpt-oss-120b
```

## Running

```bash
streamlit run app.py
```

## Usage

1. Upload a CSV file from the sidebar
2. Use the tabs to navigate:
   - **Summary**: Overview of the data
   - **Visualizations**: Create charts and graphs
   - **AI Insights**: Ask questions to the AI

## Technologies Used

- Python
- Streamlit
- LangChain
- pandas
- Plotly
- Baseten API (OpenAI-compatible)

