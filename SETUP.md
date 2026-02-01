# ViNNi Setup Guide 🛠️

This guide will help you set up **ViNNi** (Virtual Neural Network Interface) on your local Windows machine.

## Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python 3.10+**: [Download Python](https://www.python.org/downloads/)
    *   *Note: Check "Add Python to PATH" during installation.*
2.  **Git**: [Download Git](https://git-scm.com/downloads)
3.  **Ollama**: [Download Ollama](https://ollama.com/download)
    *   ViNNi uses Ollama to run LLMs locally.

---

## Installation

### 1. Clone the Repository
Open your terminal (PowerShell or Command Prompt) and run:

```powershell
git clone https://github.com/SpaceSpectre/ViNNi.git
cd ViNNi
```

### 2. Set Up Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate
```

*You should see `(venv)` appear at the start of your command line.*

### 3. Install Dependencies
Install the required Python packages:

```powershell
pip install -r requirements.txt
```

---

## Model Setup

ViNNi is optimized for **Llama 3.1** and **Qwen 2.5**. You need to pull these models via Ollama.

Ensure Ollama is running (check your system tray), then run:

```powershell
# Pull Main Model (Recommended)
ollama pull llama3.1

# Pull Fallback/Alternative Model (Optional)
ollama pull qwen2.5:7b
```

---

## Usage

To start ViNNi, simply run:

```powershell
python main.py
```

### Interactive Menu
Upon launch, ViNNi will ask you to select a model:
- **Option 1**: Llama 3.1 (8B) - Optimized for logical reasoning and math.
- **Option 2**: Qwen 2.5 (7B) - Balanced performance.

### Features
- **General Chat**: Natural conversation.
- **Math Engine**: Types queries like "$1000 at 5% for 10 years" or "Probability of 3 heads" for deterministic answers.
- **System Commands**:
    - `!help`: Show available commands.
    - `!tone [casual|professional|executive]`: Change persona.
    - `exit`: Quit the application.

---

## Troubleshooting

- **"Ollama not found"**: Ensure Ollama is installed and running in the background.
- **ModuleNotFoundError**: Ensure you activated the virtual environment (`.\venv\Scripts\activate`) before running `main.py`.
- **Finance/Math Errors**: ViNNi v0.4.0+ uses a deterministic engine. If you see erratic math, ensure you are using keywords like "calculate", "invest", "odds", or "probability".
