# Thesaurus Cleaning System

This project uses an Ollama-hosted LLM to review and clean name cluster groupings in `.the` thesaurus files.

## Setup

1. **Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Ollama**:
   Ensure you have [Ollama](https://ollama.ai/) installed and running locally. With 64GB RAM, it is recommended to use one of the following:
   - **Llama 3.1 (8B)**: Fast and reliable.
     ```bash
     ollama pull llama3.1
     ```
   - **Llama 3.3 (70B)**: Most accurate, fits in 64GB RAM (using 4-bit quantization).
     ```bash
     ollama pull llama3.3
     ```
   - **Mistral Small (24B)**: Good balance of speed and entity precision.
     ```bash
     ollama pull mistral-small
     ```

## Usage

Run the cleaning script and optionally specify the model:

```bash
python clean_thesaurus.py factory_working_example_group_normalized_30122025.the --model llama3.3
```

## How it Works

The script parses the `.the` file (UTF-16 encoded) and groups aliases under their headers. It then sends each group to the LLM (via Ollama) to identify outliers based on the logic defined in `agents.md`.

### Core Logic & Enhancements
- **Algorithmic Pre-filtering**: Uses Jaccard-like string similarity and generic word detection to flag suspicious entries before the LLM review.
- **One-Word Variance**: Explicitly rejects aliases that share only a single generic word (e.g., "Shanghai Pharma" vs "Pharma Global").
- **Chain-of-Thought Auditing**: Instructs the model to perform step-by-step mental verification for better entity resolution.
- **Distinctive Names**: Keep names sharing a distinctive root.
- **Generic Names**: Remove names that only share a generic term (e.g., "Pharma").
- **Specific Entities**: Distinguish between similar entities like NYU and SUNY.

