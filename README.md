# CV Information Extractor

**CV Information Extractor** is an automated pipeline for extracting structured, machine-readable data from CVs and resumes in PDF, DOCX, and TXT formats. It leverages OpenAI's GPT models and a customizable schema to transform unstructured documents into clean JSON, ready for analytics, search, or further processing.

---

## Key Features
- **Multi-format support:** PDF, DOCX, and TXT files
- **Batch or single file processing:** Process a single CV or entire folders
- **Robust extraction:** Uses OpenAI GPT models for accurate entity and field extraction
- **Extensible schema:** Powered by Pydantic models, easily adapt the schema to your needs
- **Standardized output:** Produces clean, consistent JSON for each CV
- **Error handling & logging:** Clear logs and robust error reporting

---

## How It Works
1. **Document Loading:** Documents are loaded and parsed using format-specific loaders.
2. **Extraction Pipeline:** Each document is sent through an extraction pipeline powered by OpenAI models, guided by a schema and prompt template.
3. **Postprocessing:** Extracted data is optionally postprocessed and validated.
4. **Output:** Results are saved as JSON, with one file per CV or a batch output for directories.

---

## Features

- Extracts key information from CVs including personal details, professional experience, education, skills, certifications, and more
- Supports multiple document formats (PDF, DOCX, TXT)
- Uses OpenAI's GPT models for accurate, robust information extraction
- Outputs structured JSON data following a standardized, extensible schema
- Can process multiple CVs in batch mode
- Handles errors gracefully and provides detailed logging
- Schema and extraction logic are easily extensible (using Pydantic models)

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your OpenAI API key in a `.env` file (in the project root):
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

---

## Web App (Streamlit)

**API Key Security Notice:**
- When using the web app, you will be asked to enter your OpenAI API key in the sidebar if it is not already set via environment variables.
- Your API key is used only for making requests to the OpenAI API during your current session. It is never shared, logged, or stored long-term by this app.
- For your security and privacy, the key is kept in memory only for your session and is cleared when you close or refresh the app.
- You can safely enter your own API key each time you use the app.

You can use the project via a web interface powered by Streamlit:

### Launch the App
```bash
streamlit run app/app.py
```

- Upload one or more documents (PDF, DOCX, TXT)
- Select the schema you want to use for extraction (e.g., CV, Invoice)
- Enter your OpenAI API key if prompted
- View and download extracted data in JSON, CSV, or Excel format

### Flexible Schema System
- The app supports multiple extraction schemas (e.g., CV, Invoice, etc.)
- Schemas are defined as separate Python files in `preprocess/schemas/` (e.g., `cv_schema.py`, `invoice_schema.py`)
- Each schema file must expose a `get_schema()` function returning a Pydantic model
- You can select which schema to use from the Streamlit UI
- To add a new schema, create a new file in `preprocess/schemas/` and implement `get_schema()`

---

## Quickstart (CLI)

```bash
python extract.py --input path/to/cv/folder
```
- `--input`, `-i`: Path to the file or directory containing CVs (required)

The output will be saved in an `outputs/` folder inside your input directory by default, with one JSON file per CV or a single batch file for directories.

## Architecture & Flow

1. **extract.py**: Entry point and CLI handler.
2. **run_pipeline.py**: Orchestrates the extraction process, handling both single files and directories.
3. **extractor.py**: Handles LLM-powered extraction for each document.
4. **schemas/cv_schema.py**: Defines the schema for extracted data.

---

## Output Schema

The extracted data is output as JSON following this schema (fields may be null if not present in the CV):

- `name`: Full name
- `location`: { `city`, `country`, `region` }
- `email`, `phone`: Contact info
- `profiles`: List of social/professional profiles (LinkedIn, GitHub, etc.)
- `experience_years`: Total years of professional experience (float)
- `professional_experience`: List of professional experience objects:
    - `position`: Job title/position
    - `company`: Name of the company
    - `years`: Years in this position (float, optional)
- `education`: List of education objects:
    - `institution`, `degree`, `years`, `field`
- `skills`: List of skills
- `certifications`: List of certifications
- `languages`: List of languages with proficiency

#### Example Output

```json
{
  "name": "Jane Doe",
  "location": {"city": "London", "country": "UK", "region": "Greater London"},
  "email": "jane.doe@email.com",
  "phone": "+44 1234 567890",
  "profiles": [
    {"network": "LinkedIn", "url": "https://linkedin.com/in/janedoe"}
  ],
  "experience_years": 7.5,
  "professional_experience": [
    {"position": "Software Engineer", "company": "TechCorp", "years": 2.0},
    {"position": "Junior Developer", "company": "DevStart", "years": 1.5}
  ],
  "education": [
    {"institution": "University of London", "degree": "BSc Computer Science", "years": "2016-2019", "field": "Computer Science"}
  ],
  "skills": ["Python", "Machine Learning"],
  "certifications": ["AWS Certified Developer"],
  "languages": [
    {"language": "English", "proficiency": "Native"},
    {"language": "Spanish", "proficiency": "Intermediate"}
  ]
}
```

### Output Format

The tool outputs a JSON array where each element contains the extracted information from a single CV. The output follows this schema:

```json
{
  "name": "string",
  "location": {
    "city": "string",
    "country": "string",
    "region": "string"
  },
  "email": "string",
  "phone": "string",
  "linkedin": "string",
  "experience_years": 0,
  "current_position": "string",
  "current_company": "string",
  "education": [
    {
      "degree": "string",
      "institution": "string",
      "year": "string",
      "field": "string"
    }
  ],
  "skills": ["string"],
  "languages": [
    {
      "language": "string",
      "proficiency": "string"
    }
  ],
  "certifications": ["string"],
  "source_file": "string"
}
```

## Extending the Schema

The schema is defined using [Pydantic](https://docs.pydantic.dev/) models in `cv_extractor.py`. To add or modify fields, simply update the models and adjust the system prompt as needed.

## Requirements

- Python 3.8+
- OpenAI API key (for best results)
- Required Python packages (see `requirements.txt`)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
