# EquiBench: Benchmarking Code Reasoning Capabilities of Large Language Models via Equivalence Checking

![Version](https://img.shields.io/badge/version-1.0.0-blue)
[![arXiv](https://img.shields.io/badge/arXiv-2502.12466-b31b1b.svg)](https://arxiv.org/abs/2502.12466)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.12+-yellow.svg)](https://www.python.org/downloads/)

## Overview

EquiBench is a comprehensive benchmark designed to evaluate the code reasoning capabilities of Large Language Models (LLMs) through equivalence checking tasks. This framework helps researchers and developers assess how well different LLMs understand code semantics, reason about program functionality, and determine when two code snippets are functionally equivalent despite syntactic differences.

### Key Features

- **Diverse Test Cases**: Includes 400 pairs of equivalent programs across six distinct categories (`DCE`, `STOKE`, `TVM`, `OJ_A`, `OJ_V`, `OJ_VA`)
- **Multiple Prompting Strategies**: Support for zero-shot, few-shot, and chain-of-thought variations to evaluate different reasoning approaches
- **Wide Model Support**: Compatible with leading LLMs from OpenAI, Anthropic, Meta, Mistral AI, Qwen, and DeepSeek
- **Standardized Methodology**: Consistent evaluation framework enabling fair comparison across different model architectures

## Table of Contents

- [Overview](#overview)
- Steps
  - [Initial Setup](#initial-setup)
  - [Daily Setup](#daily-setup)
  - [Step 1: Downloading Datasets](#step-1-downloading-datasets)
  - [Step 2: Running Evaluations](#step-2-running-evaluations)
- Details
  - [Dataset Structure](#dataset-structure)
  - [Supported Prompt Types](#supported-prompt-types)
  - [Supported Models](#supported-models)
  - [Evaluation Results](#evaluation-results)
- [Citation](#citation)
- [License](#license)

## Initial Setup

1. Clone the repository and navigate to the directory

    ```Shell
    git clone https://github.com/Anjiang-Wei/EquiBench.git
    cd EquiBench
    ```

2. Use Python version 3.12 or higher
  
    You can use `pyenv` to manage Python versions:

    Prerequisite: [Install pyenv](https://github.com/pyenv/pyenv)

    Install Python 3.12 using pyenv:
  
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

    Create an empty `.env` file

    ```Shell
    touch .env
    ```

    Add the following API keys to your `.env` file:

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

Execute the evaluation script with your desired configuration. The example below runs a zero-shot evaluation on three different models with a sample limit of 1 for each category:

```Shell
python step2_eval.py data result/eval \
    --prompt_types ZERO \
    --models \
    openai/gpt-4o-mini-2024-07-18 \
    anthropic/claude-3-5-sonnet-20241022 \
    Qwen/Qwen2.5-7B-Instruct-Turbo \
    --limit 1
```

### Additional Options

The evaluation script supports several command-line options:

- `--models`: List of models to evaluate (see [Supported Models](#supported-models))
- `--limit`: Number of test pairs to evaluate per category (omit to evaluate all 400 pairs per category)
- `--prompt_types`: Types of prompting strategies to use (see [Supported Prompt Types](#supported-prompt-types))
- `--categories`: Select specific categories for evaluation. Choices: `DCE`, `STOKE`, `TVM`, `OJ_A`, `OJ_V`, `OJ_VA`
- `--prompt_path`: Path to custom prompt templates, default as `prompts.toml`
- `--log_level`: Set logging verbosity, default as `INFO`. Choices: `DEBUG`, `INFO`, `WARNING`, `ERROR`

### Example Commands

```Shell
# Evaluate all models on a single category with few-shot prompting
python step2_eval.py data result/eval --prompt_types FEW --categories OJ_A --limit 10

# Evaluate one model on all categories with chain-of-thought reasoning
python step2_eval.py data result/eval --prompt_types ZERO_COT --models openai/gpt-4o-2024-11-20

# Custom logging and output directory
python step2_eval.py data custom_results --prompt_types ZERO FEW
```

## Dataset Structure

EquiBench contains six distinct categories of code equivalence tasks:

- **DCE (Dead Code Elimination)**: Code pairs that differ by removal of unused code
- **STOKE (Superoptimizer Toolkit for Equality)**: Assembly code pairs optimized using the STOKE framework
- **TVM (Tensor Virtual Machine)**: Code pairs optimized for tensor operations
- **OJ_A (Online Judge - Algorithm)**: Different algorithmic solutions to the same programming problem
- **OJ_V (Online Judge - Variables)**: Code pairs with variable renaming transformations
- **OJ_VA (Online Judge - Variables and Algorithms)**: Code pairs with both variable renaming and algorithmic differences

Each category contains 400 pairs of programs that are functionally equivalent but syntactically different, providing a diverse range of challenges for LLMs to reason about code semantics.

## Supported Prompt Types

EquiBench evaluates models using four different prompting strategies:

- `ZERO`: Zero-shot prompting (directly asking the model without examples)
- `FEW`: Few-shot prompting (providing example problems and solutions)
- `ZERO_COT`: Zero-shot chain of thought (encouraging step-by-step reasoning)
- `FEW_COT`: Few-shot chain of thought (examples with step-by-step reasoning)

Each strategy tests different aspects of a model's reasoning capabilities, from basic understanding to advanced reasoning chains.

## Supported Models

EquiBench supports evaluation across a diverse range of LLMs:

### OpenAI Models

```Shell
openai/o1-mini-2024-09-12
openai/gpt-4o-2024-11-20
openai/gpt-4o-mini-2024-07-18
openai/o3-mini-2025-01-31
```

### Anthropic Models

```Shell
anthropic/claude-3-5-sonnet-20241022
```

### Meta (Llama) Models

```Shell
meta-llama/Llama-3.2-3B-Instruct-Turbo
meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo
meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo
```

### Mistral AI Models

```Shell
mistralai/Mistral-7B-Instruct-v0.3
mistralai/Mixtral-8x7B-Instruct-v0.1
mistralai/Mixtral-8x22B-Instruct-v0.1
```

### Qwen Models

```Shell
Qwen/Qwen2.5-7B-Instruct-Turbo
Qwen/Qwen2.5-72B-Instruct-Turbo
Qwen/QwQ-32B-Preview
```

### DeepSeek Models

```Shell
deepseek-ai/DeepSeek-R1
deepseek-ai/DeepSeek-V3
```

Additional models from OpenAI, Anthropic, and together.ai platforms are also supported.

## Evaluation Results

Below is a summary of performance across different models and prompting strategies based on our paper experiments:

*Note: These results represent average accuracy across all categories. For detailed results, please refer to our [paper](https://arxiv.org/pdf/2502.12466).*

## Citation

If you use EquiBench in your research, please cite our paper:

[**Paper Link**](https://arxiv.org/pdf/2502.12466)

```plaintext
@article{wei2025equibench,
  title={EquiBench: Benchmarking Code Reasoning Capabilities of Large Language Models via Equivalence Checking},
  author={Wei, Anjiang and Cao, Jiannan and Li, Ran and Chen, Hongyu and Zhang, Yuhui and Wang, Ziheng and Sun, Yaofeng and Liu, Yuan and Teixeira, Thiago S. F. X. and Yang, Diyi and Wang, Ke and Aiken, Alex},
  journal={arXiv preprint arXiv:2502.12466},
  year={2025}
}
```

## License

Apache License 2.0. See the [LICENSE](LICENSE) file for details.
