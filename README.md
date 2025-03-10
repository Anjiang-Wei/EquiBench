# EquiBench

## Table of Contents

- [Initial Setup](#initial-setup)
- [Daily Setup](#daily-setup)
- [Step 1: Downloading Datasets](#step-1-downloading-datasets)
- [Step 2: Running Evaluations](#step-2-running-evaluations)

## Initial Setup

1. Clone the repository and navigate to the directory

    ```Shell
    git clone https://github.com/Anjiang-Wei/EquiBench.git
    cd EquiBench
    ```

2. Use Python version 3.12 or higher

    ```Shell
    pyenv install 3.12
    pyenv local 3.12
    ```

3. Create a virtual environment and activate it

    ```Shell
    python -m venv .venv
    source .venv/bin/activate
    ```

4. Update pip and install required packages

    ```Shell
    pip install --upgrade pip
    pip install .
    ```

5. Set up API keys in a `.env` file:

    ```Shell
    touch .env
    ```

6. Add the following API keys to your `.env` file:

    ```Shell
    OPENAI_API_KEY=<your OpenAI key here>
    ANTHROPIC_API_KEY=<your Anthropic key here>
    TOGETHER_API_KEY=<your Together key here>
    HF_TOKEN=<your HuggingFace access token here>
    ```

## Daily Setup

When returning to work on EquiBench:

1. Navigate to the repository directory

    ```Shell
    cd EquiBench
    ```

2. Activate the virtual environment

    ```Shell
    source .venv/bin/activate
    ```

## Step 1: Downloading Datasets

1. Obtain a `read` or `write` type [access token from HuggingFace](https://huggingface.co/settings/tokens)

2. Login using the access token:

    **Option A**: Log in via command line and verify access:

    ```Shell
    huggingface-cli login
    huggingface-cli whoami
    ```

    **Option B**: Add your token directly to the `.env` file as the `HF_TOKEN` environment variable.

3. Download the datasets:

    ```Shell
    python step1_data.py data
    ```

## Step 2: Running Evaluations

Execute the evaluation script with your desired configuration:

```Shell
python step2_eval.py data result/eval \
    --prompt_types ZERO \
    --models \
    openai/gpt-4o-mini-2024-07-18 \
    anthropic/claude-3-5-sonnet-20241022 \
    Qwen/Qwen2.5-7B-Instruct-Turbo \
    --limit 1
```

- Supported Prompt Types

    The following prompt types are supported:
  - `ZERO`: Zero-shot prompting
  - `FEW`: Few-shot prompting
  - `ZERO_COT`: Zero-shot chain of thought
  - `FEW_COT`: Few-shot chain of thought

- Supported Models

    EquiBench has been evaluated on the following models:

  - OpenAI

    ```Shell
    openai/o1-mini-2024-09-12
    openai/gpt-4o-2024-11-20
    openai/gpt-4o-mini-2024-07-18
    openai/o3-mini-2025-01-31
    ```

  - Anthropic

    ```Shell
    anthropic/claude-3-5-sonnet-20241022
    ```

  - Meta (Llama)

    ```Shell
    meta-llama/Llama-3.2-3B-Instruct-Turbo
    meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo
    meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
    meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo
    ```

  - Mistral AI

    ```Shell
    mistralai/Mistral-7B-Instruct-v0.3
    mistralai/Mixtral-8x7B-Instruct-v0.1
    mistralai/Mixtral-8x22B-Instruct-v0.1
    ```

  - Qwen

    ```Shell
    Qwen/Qwen2.5-7B-Instruct-Turbo
    Qwen/Qwen2.5-72B-Instruct-Turbo
    Qwen/QwQ-32B-Preview
    ```

  - DeepSeek

    ```Shell
    deepseek-ai/DeepSeek-R1
    deepseek-ai/DeepSeek-V3
    ```
