# ViNNi - Local AI Chatbot

ViNNi is a local AI chatbot designed to run efficiently on your laptop using Ollama. It serves as a personal assistant, capable of natural conversation and information retrieval, similar to Siri but fully local and private.

## Features
- **Local Privacy**: Runs entirely on your machine.
- **Multi-Model Support**: Choose between Llama 3.1 (Optimized) and Qwen 2.5 at startup.
- **Custom Persona**: "ViNNi", created by Abhishek Arora.
- **Streaming Responses**: Real-time text generation.

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

### Model Selection
Upon starting, you will be prompted to choose a model:
1.  **Llama 3.1 (8B)**: Optimized with custom parameters (Context: 8k, Temp: 0.6) for best performance.
2.  **Qwen 2.5 (7B)**: Uses default settings.
3.  **Custom**: Type the name of any other model you have installed in Ollama.
