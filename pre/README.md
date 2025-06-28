# CV Information Extractor

This tool automatically extracts structured information from CVs and resumes (PDF, DOCX, TXT) and outputs the data in a standardized JSON format.

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

## Usage

Run the extractor on your CV files as described in the example usage in `cv_extractor.py`.

### Basic Usage

```bash
python main_extract.py -i path/to/cv/folder -o output.json
```

### Command Line Arguments

- `-i, --input`: Path to the directory containing CVs (required)
- `-o, --output`: Output JSON file path (default: cv_extraction_results.json)
- `--openai-key`: OpenAI API key (can also be set via .env file)

### Example

```bash
# Process all CVs in the 'cvs' folder and save to 'results.json'
python main_extract.py -i ./cvs -o results.json
```

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
