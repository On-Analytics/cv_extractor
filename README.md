# Extraction_Agent

## Overview
This tool extracts structured data from documents (PDF, DOCX, TXT) placed in a folder, using advanced AI extraction logic. Outputs are saved automatically.

## Quick Start (For Clients)

### 1. Place Your Documents
- Put all documents you want to process in the `documents_folder` directory in the project root.
- Supported formats: PDF, DOCX, DOC, TXT

### 2. Install Requirements
Open a terminal in the project folder and run:
```sh
pip install -r requirements.txt
```

### 3. Set Your OpenAI API Key
- Create a `.env` file in the project root with the following line:
  ```
  OPENAI_API_KEY=sk-...your-key...
  ```
- Or set the environment variable `OPENAI_API_KEY` in your system.

### 4. Run the Extraction
From the project root, run:
```sh
python extract.py
```

### 5. Find Your Results
- Extracted results: `outputs/extraction_results.json`
- Postprocessed results: `outputs/pos_extraction_results.json`

---

## Project Structure
- `extract.py` — Main script to run extraction and postprocessing (run this!)
- `documents_folder/` — Place your documents here
- `outputs/` — Output files are saved here
- `preprocessing/` — Extraction logic and schemas

## Troubleshooting
- Make sure your Python version is 3.8 or higher.
- If you have issues, ensure all dependencies are installed and your API key is valid.
- For further help, contact On-Analytics support.
