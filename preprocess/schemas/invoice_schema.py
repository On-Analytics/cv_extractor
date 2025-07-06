from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
import re
from datetime import datetime

# Load environment variables from .env in parent directory
from dotenv import load_dotenv
import os
from pathlib import Path
# Find the project root (where .env is located)
project_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

class InvoiceItem(BaseModel):
    description: Optional[str] = Field(None, description="Description of the item or service")
    quantity: Optional[int] = Field(None, description="Quantity of the item or service")
    unit_price: Optional[float] = Field(None, description="Unit price of the item or service")
    total: Optional[float] = Field(None, description="Total price for the item or service (quantity * unit_price)")

class DocumentSchema(BaseModel):
    invoice_number: Optional[str] = Field(None, description="Invoice number")
    date: Optional[str] = Field(None, description="Invoice date")
    vendor: Optional[str] = Field(None, description="Vendor or seller name")
    customer: Optional[str] = Field(None, description="Customer or buyer name")
    items: List[InvoiceItem] = Field(default_factory=list, description="List of items or services in the invoice")
    total_amount: Optional[float] = Field(None, description="Total amount for the invoice")

    @field_validator('items', mode='before')
    def empty_list_if_none(cls, v):
        """If 'items' is None, convert it to an empty list before validation."""
        if v is None:
            return []
        return v

def get_schema():
    return DocumentSchema

def get_prompt():
    return (
        """
Follow these instructions:

- DO NOT extract or include any other fields.
- Do NOT guess or infer values.
- Do NOT use placeholders like 'N/A', 'Not specified', etc.
- Output must be a valid JSON object with ONLY the fields above (even if all are null or empty arrays).


Extract ONLY the following fields as a JSON object with this structure:
{{
  "invoice_number": str or null,
  "date": str or null,
  "vendor": str or null,
  "customer": str or null,
  "items": [
    {{
      "description": str or null,
      "quantity": int or null,
      "unit_price": float or null,
      "total": float or null
    }}
  ],
  "total_amount": float or null
}}

Passage:
{input}
"""
    )