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

## Quickstart

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
