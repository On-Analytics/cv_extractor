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

- Extracts key information from a variety of document types (CVs, invoices, etc.)
- Flexible schema system: easily add support for new document types by defining a schema
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
- Schemas are defined as separate Python files in `preprocess/schemas/` (e.g., `cv_schema.py`, `invoice_schema.py`, `contract_schema.py`)
- Each schema file must expose a `get_schema()` function returning a Pydantic model
- You can select which schema to use from the Streamlit UI
- To add a new schema (for any document type), create a new file in `preprocess/schemas/` and implement `get_schema()`
- The extraction logic is schema-agnostic: only the selected schema determines the fields and structure of the output

**Example:**
- To extract data from invoices, add `invoice_schema.py` with a Pydantic model for invoice fields (e.g., invoice number, total, date, line items)
- To extract data from contracts, add `contract_schema.py` with the relevant fields

This makes the extractor extensible for any structured document extraction use-case.

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

The extracted data is output as JSON following the schema for the selected document type. Each schema is defined in its own file (e.g., `cv_schema.py`, `invoice_schema.py`), and the output fields will match those defined in the selected schema.

### Example: CV Schema

- `name`: Full name
- `location`: { `city`, `country`, `region` }
- `email`, `phone`: Contact info
- ... (see schema file for full list)

#### Example Output (CV)
```json
{
  "name": "Jane Doe",
  "location": {"city": "London", "country": "UK", "region": "Greater London"},
  "email": "jane.doe@email.com",
  ...
}
```

### Example: Invoice Schema

- `invoice_number`: Invoice number
- `date`: Invoice date
- `vendor`: Vendor name
- `customer`: Customer name
- `total`: Total amount
- `line_items`: List of line items (description, quantity, unit price, amount)

#### Example Output (Invoice)
```json
{
  "invoice_number": "INV-12345",
  "date": "2024-06-30",
  "vendor": "Acme Corp",
  "customer": "Beta LLC",
  "total": 1250.00,
  "line_items": [
    {"description": "Widget A", "quantity": 10, "unit_price": 50, "amount": 500},
    {"description": "Widget B", "quantity": 5, "unit_price": 150, "amount": 750}
  ]
}
```

### Output Format

The tool outputs a JSON array where each element contains the extracted information from a single document. The output format is entirely determined by the selected schema.

## Extending the Schema

Schemas are defined using [Pydantic](https://docs.pydantic.dev/) models in the `preprocess/schemas/` directory. To add or modify fields, simply update or create a schema file and implement the `get_schema()` function. The extraction logic will automatically use the selected schema for all processing.

## Requirements

- Python 3.8+
- OpenAI API key (for best results)
- Required Python packages (see `requirements.txt`)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
