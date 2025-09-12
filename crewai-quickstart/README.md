# CrewAI Quickstart Project

This is a CrewAI project that demonstrates the basic usage of CrewAI framework for creating AI agent crews. The project includes two agents that work together to research a topic and create a detailed report.

## Features

- **Researcher Agent**: Conducts thorough research on any given topic using web search capabilities
- **Reporting Analyst**: Creates comprehensive reports based on research findings
- **Configurable**: Easy to customize agents and tasks through YAML configuration files
- **Command-line Interface**: Run the crew with custom topics from the command line

## Project Structure

```
crewai-quickstart/
├── src/
│   └── crewai_quickstart/
│       ├── config/
│       │   ├── agents.yaml      # Agent configurations
│       │   └── tasks.yaml       # Task configurations
│       ├── __init__.py
│       ├── crew.py              # Main crew implementation
│       └── main.py              # Entry point
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup

### Prerequisites

1. **Install Ollama**: Download and install from [ollama.com](https://ollama.com)
2. **Pull a model**: Run `ollama pull llama3.2` (or your preferred model)

### Project Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd crewai-quickstart
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file to configure:
   - `OLLAMA_MODEL`: The model to use (default: llama3.2)
   - `OLLAMA_BASE_URL`: Ollama server URL (default: http://localhost:11434)
   - `SERPER_API_KEY`: (Optional) For web search functionality - get from [serper.dev](https://serper.dev)

5. **Start Ollama** (if not already running):
   ```bash
   ollama serve
   ```

## Usage

### Basic Usage

Run the crew with the default topic (AI LLMs):

```bash
python src/crewai_quickstart/main.py
```

### Custom Topic

Run the crew with a custom research topic:

```bash
python src/crewai_quickstart/main.py "Climate Change Technologies"
```

### Output

The crew will:
1. Research the specified topic using web search
2. Generate a detailed report based on the research
3. Save the report as `report.md` in your current directory

## Configuration

### Agents (`src/crewai_quickstart/config/agents.yaml`)

- **researcher**: A senior data researcher that uncovers cutting-edge developments
- **reporting_analyst**: A meticulous analyst that creates detailed reports

### Tasks (`src/crewai_quickstart/config/tasks.yaml`)

- **research_task**: Conducts thorough research and returns 10 bullet points
- **reporting_task**: Creates a comprehensive report based on research findings

## Customization

You can easily customize the project by:

1. **Modifying agent roles and backstories** in `agents.yaml`
2. **Changing task descriptions and expected outputs** in `tasks.yaml`
3. **Adding new tools** to agents in `crew.py`
4. **Adjusting the crew process** (sequential, hierarchical, etc.)

## Configuration

### Required
- **Ollama**: Local LLM server running with a downloaded model (e.g., llama3.2)

### Optional
- **SERPER_API_KEY**: Free web search API (get from [serper.dev](https://serper.dev)) for enhanced research capabilities

### Supported Ollama Models
- llama3.2 (default)
- llama3.1
- mistral
- codellama
- And any other model available in Ollama

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.