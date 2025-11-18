# Data Analysis AI 📊

AI-powered data analysis project using Streamlit, LangChain, and Baseten API

## Features

- 📁 Upload and automatically analyze CSV files
- 🤖 AI-powered data analysis and question answering
- 📈 Create interactive visualizations using Plotly
- 🔍 Automatic data analysis
- 💻 Execute Python code directly for custom analysis
- 🚀 Production-ready with Docker support
- 📊 Comprehensive logging and error handling
- 🔒 Security features and validation

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
│   ├── analysis_engine.py   # Analysis engine
│   ├── logger.py            # Logging system
│   ├── exceptions.py        # Custom exceptions
│   └── health_check.py      # Health check utilities
├── config.py          # Configuration
├── app.py             # Main entry point
├── .env               # Environment variables
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose setup
└── requirements.txt   # Required libraries
```

## Installation

### Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Setup `.env` file:
   - Copy `env.example` to `.env`
   - Or create `.env` manually and add:
```env
ENV=development
DEBUG=True
BASETEN_API_KEY=your_api_key_here
BASETEN_BASE_URL=https://inference.baseten.co/v1
BASETEN_MODEL=openai/gpt-oss-120b
```

3. Run the application:
```bash
streamlit run app.py
```

### Production with Docker

1. Configure environment:
```bash
cp env.example .env
# Edit .env with production settings
```

2. Build and run:
```bash
docker-compose up -d
```

3. Check logs:
```bash
docker-compose logs -f
```

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

## Usage

1. Upload a CSV file from the sidebar
2. Use the tabs to navigate:
   - **Summary**: Overview of the data
   - **Visualizations**: Create charts and graphs
   - **AI Insights**: Ask questions to the AI

## Configuration

### Environment Variables

- `ENV`: Environment (development/production)
- `DEBUG`: Debug mode (True/False)
- `BASETEN_API_KEY`: Baseten API key (required)
- `BASETEN_BASE_URL`: Baseten API base URL
- `BASETEN_MODEL`: Model name
- `MAX_FILE_SIZE_MB`: Maximum file size in MB (default: 100)
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)
- `STREAMLIT_SERVER_PORT`: Server port (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Server address (default: 0.0.0.0)

See `env.example` for all available options.

## Production Features

- ✅ Comprehensive error handling
- ✅ Structured logging with rotation
- ✅ Health check endpoints
- ✅ Docker containerization
- ✅ Security validations
- ✅ File size limits
- ✅ Performance monitoring
- ✅ Environment-based configuration

## Technologies Used

- Python 3.11+
- Streamlit
- LangChain
- pandas
- Plotly
- Baseten API (OpenAI-compatible)
- Docker
- psutil

## Logging

Logs are stored in `logs/app.log` with automatic rotation:
- Max file size: 10MB
- Backup count: 5 files
- Log levels: DEBUG, INFO, WARNING, ERROR

## Health Checks

The application includes health check functionality. Check system status:

```python
from back.health_check import check_health, get_system_info

health = check_health()
system_info = get_system_info()
```

## Troubleshooting

1. **Application won't start**: Check logs in `logs/app.log`
2. **LLM API errors**: Verify API key and network connectivity
3. **File upload issues**: Check file size limits in configuration
4. **Memory issues**: Reduce `MAX_FILE_SIZE_MB` and `MAX_ROWS_PREVIEW`

## License

MIT License

## Support

For issues and questions:
1. Check the logs: `tail -f logs/app.log`
2. Review [DEPLOYMENT.md](DEPLOYMENT.md) for deployment issues
3. Check health status using health check utilities
