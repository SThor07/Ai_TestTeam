# Ai_TestTeam: AI-Powered Android QA Automation Framework

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

TesterBeta is an intelligent framework for automating Android QA testing using a multi-agent architecture powered by LLMs. It combines planning, execution, verification, and supervision to create robust, self-improving test automation.

## 🌟 Features

- **Multi-Agent Architecture**: Specialized agents for planning, execution, verification, and supervision
- **LLM-Powered Intelligence**: Uses large language models to understand test goals and adapt to UI changes
- **Android Environment Integration**: Works with Android World for realistic device simulation
- **Dynamic Replanning**: Automatically adjusts test plans when verification fails
- **Supervision & Improvement**: Generates reports with suggestions for test improvement

## 🏗️ Architecture

QualGent uses a multi-agent architecture with the following components:

1. **Planner Agent**: Breaks down high-level goals into specific subgoals
2. **Executor Agent**: Interacts with the Android environment to execute subgoals
3. **Verifier Agent**: Validates if each execution step achieved its intended purpose
4. **Supervisor Agent**: Reviews test episodes and suggests improvements
5. **QA Loop**: Orchestrates the interaction between agents

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- [Ollama](https://ollama.ai/) for local LLM inference
  - **Linux/macOS**: Install Ollama CLI: `curl -fsSL https://ollama.com/install.sh | sh`
  - **Windows**: Download and install from [Ollama's website](https://ollama.ai/download)
- Android World environment

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/QualGent.git
   cd QualGent
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the Ollama server (if not already running):

   ```bash
   # On Linux/macOS
   ollama serve
   # To run in background: nohup ollama serve > ollama.log 2>&1 &

   # On Windows, Ollama runs as a service after installation
   # You can check it's running in your system tray
   ```

5. Pull the required LLM model with Ollama:
   ```bash
   ollama pull llama3
   ```

## 🔧 Configuration

Edit `configs/default.yaml` to customize your setup:

```yaml
# LLM configuration
llm:
  provider: "ollama"
  model: "llama3" # make sure you pulled it with `ollama pull llama3`
  base_url: "http://localhost:11434"
  temperature: 0.2
  max_tokens: 512

# Android environment configuration
android_world:
  task: "settings_wifi" # clock_alarm, email_search, etc.
  render_rgb: true
```

## 📱 Running Tests

Use the `run_task.py` script to execute tests:

```bash
python scripts/run_task.py --goal "Test turning Wi-Fi on and off" --task "settings_wifi"
```

Options:

- `--goal`: The high-level test goal (required)
- `--task`: The Android task to test (defaults to config value)
- `--config`: Path to configuration file (defaults to `configs/default.yaml`)
- `--llm.model`: Override the LLM model from config

## 📊 Reports

After test execution, QualGent generates reports in the `reports/` directory with insights and improvement suggestions from the Supervisor Agent.

## 🧪 Writing Tests

Create test files in the `tests/` directory. See `tests/test_settings_wifi.py` for an example.

## 🔍 Troubleshooting

### Ollama Issues

- **Connection refused error**: Make sure Ollama server is running. Check with `curl http://localhost:11434/api/version`
- **Model not found**: Ensure you've pulled the model with `ollama pull llama3`
- **Slow responses**: Try a smaller model like `ollama pull mistral:7b`
- **Out of memory**: Reduce model size or increase your system's RAM/swap space
## ✅ Final Working Demo Screenshots

### 🔹 Screenshot 1
![Final Working 1](https://raw.githubusercontent.com/SThor07/Ai_TestTeam/main/Final_Working1.png)

### 🔹 Screenshot 2
![Final Working 2](https://raw.githubusercontent.com/SThor07/Ai_TestTeam/main/Final_Working2.png)
---

Built with ❤️ for better Android QA automation and test improvement.
