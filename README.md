# EquiBench

## Initial Setup

1. Clone the repository and navigate to the directory

    ```Shell
    git clone https://github.com/Anjiang-Wei/EquiBench.git
    cd EquiBench
    ```

2. Use Python version >= 3.12

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

5. Create a `.env` file to store API keys:

    ```Shell
    touch .env
    ```

6. Add the following API keys to your `.env` file:

    ```Shell
    OPENAI_API_KEY=
    ANTHROPIC_API_KEY=
    TOGETHER_API_KEY=
    HF_TOKEN=
    ```

## Daily Setup

1. Navigate to the repository directory

    ```Shell
    cd EquiBench
    ```

2. Activate the virtual environment

    ```Shell
    source .venv/bin/activate
    ```

## Step 1: Download Datasets

1. Obtain a `read` or `write` access token from HuggingFace

    a. You can directly log in to HuggingFace using the command line and test whether you are logged in successfully:

    ```Shell
    huggingface-cli login
    huggingface-cli whoami
    ```

    b. Alternatively, you can write your access token directly into the `.env` file as the `HF_TOKEN` environment variable.

2. Run the command line:

    ```Shell
    python step1_data.py data
    ```

## Step 2: Evaluation

1. Run the command line:

    ```Shell
    python step2_eval.py data result/eval \
      --prompt_types ZERO \
      --models \
        openai/gpt-4o-mini-2024-07-18 \
        anthropic/claude-3-5-sonnet-20241022 \
        Qwen/Qwen2.5-7B-Instruct-Turbo \
      --limit 1
    ```
