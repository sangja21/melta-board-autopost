# Python Development Environment Setup

This project uses **Conda** for environment management to ensure reproducibility and isolation.

## 1. Prerequisites
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/) installed.

## 2. Setting up the Environment

### Create and Activate Environment
Run the following commands to create a new environment named `melta-bot` with Python 3.11:

```bash
# Create environment
conda create -n melta-bot python=3.11 -y

# Activate environment
conda activate melta-bot
```

### Install Dependencies
With the environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

## 3. Environment Variables
Create a `.env` file in the root directory (already added to .gitignore) with the following keys:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
OPENAI_API_KEY=sk-...
```

## 4. Running the Bot
To run the auto-post bot locally:

```bash
python scripts/autopost.py
```

## 5. Exporting Environment (Optional)
If you add new dependencies, update `requirements.txt`:

```bash
pip freeze > requirements.txt
```
