# ViNNi - Local AI Chatbot

ViNNi is a local AI chatbot designed to run efficiently on your laptop using Ollama. It serves as a personal assistant, capable of natural conversation and information retrieval, similar to Siri but fully local and private.

**Current Version**: `v0.3.0` (Math Engine Architecture)

## Features
- **Local Privacy**: Runs entirely on your machine.
- **Strict & Stable**: Defined capability contract (CHAT, CODE, ANALYSIS, DOCUMENT).
- **Performance**:
- **Performance**:
    - **Smart Caching**: In-memory cache provides 0ms latency for repeated questions (`CHAT`, `CODE`, `ANALYSIS` aware).
    - **Dynamic Tone**: Switch between `Casual`, `Professional`, and `Executive` styles on the fly.
    - **Answer Only Mode**: Use "just answer" to skip explanations.
- **Observability Layer**: All interactions logged to `vinni.log` in structured JSONL.
- **Analytics**: Built-in dashboard to track efficiency (`scripts/analyze_metrics.py`).
- **CLI Commands**:
    - `!help`: Show supported intents and usage.
    - `!version`: Show current system version.
    - `!tone`: Switch personality (`!tone casual/executive`).
- **Governance**:
    - [Security Policy](SECURITY.md)
    - [Contributing Guidelines](CONTRIBUTING.md)
    - [License (Non-Commercial)](LICENSE.md)

## Prerequisites
1.  **Python 3.8+**
2.  **Ollama**: Must be installed and running in the background. [Download Ollama](https://ollama.com/)

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/SpaceSpectre/ViNNi.git
    cd ViNNi
    ```

2.  **Create and Activate Virtual Environment**:
    ```powershell
    # Windows
    python -m venv venv
    .\venv\Scripts\Activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Pull Required Models**:
    ```bash
    ollama pull llama3.1
    ollama pull qwen2.5
    ```

## Usage

Run the main script to start the chatbot:
```bash
python main.py
```

### Commands
- Type `!help` inside the chat to see valid intents.
- Type `!version` to check the running version.
- Type `exit` or `quit` to close.

### Model Selection
Upon starting, you will be prompted to choose a model:
1.  **Llama 3.1 (8B)**: Optimized with custom parameters (Context: 8k, Temp: 0.6) for best performance.
2.  **Qwen 2.5 (7B)**: Uses default settings.
3.  **Custom**: Type the name of any other model you have installed in Ollama.

### Analytics Dashboard
To view performance metrics (Cache Hit Rate, Top Queries, Latency):
```powershell
python scripts/analyze_metrics.py
```
This generates a report object and saves detailed stats to `metrics.json`.
