from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
import re
from datetime import datetime
from pydantic import field_validator

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
    date: Optional[str] = Field(None, description="Invoice date formatted as 'YYYY-MM-DD'")
    vendor: Optional[str] = Field(None, description="Vendor or seller name")
    customer: Optional[str] = Field(None, description="Customer, client or buyer name")
    items: List[InvoiceItem] = Field(default_factory=list, description="List of items or services in the invoice")
    subtotal: Optional[float] = Field(None, description="Subtotal amount before tax")
    tax: Optional[float] = Field(None, description="Tax amount")
    total_amount: Optional[float] = Field(None, description="Total amount for the invoice (including tax)")

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

You are an invoice extraction assistant:

**Rules**:
- Do **NOT** guess or infer missing values.
- Do **NOT** use placeholders like "N/A", "Unknown", or "Not specified".
- Output must be a **valid JSON object** using ONLY the fields defined in the schema (see below).
- Match invoice numbers from phrases like: "Invoice No", "No. de factura", "Factura Electrónica", etc 

**Examples**:

Example 1:
Passage:
Acme Supplies Inc.
123 Main Street, Springfield

Invoice No: INV-2024-001
Date: 2024-06-15

Bill To: Beta Corp.
456 Elm Avenue, Metropolis

Items:
- Laser Printer x2 @ $199.99 each
- Printer Paper (Box) x5 @ $25.00 each

Subtotal: $524.98
Tax: $41.99
Total: $566.97

Output:
{{
  "invoice_number": "INV-2024-001",
  "date": "2024-06-15",
  "vendor": "Acme Supplies Inc.",
  "customer": "Beta Corp.",
  "items": [
    {{
      "description": "Laser Printer",
      "quantity": 2,
      "unit_price": 199.99,
      "total": 399.98
    }},
    {{
      "description": "Printer Paper (Box)",
      "quantity": 5,
      "unit_price": 25.00,
      "total": 125.00
    }}
  ],
  "subtotal": 524.98,
  "tax": 41.99,
  "total_amount": 566.97
}}

Example 2:
Passage:
Consulting Solutions LLC
789 Market Road, Capital City

Factura Electrónica: 2025-07-0098
Fecha: 2025-07-01

Cliente: Omega Enterprises
321 Oak Lane, Gotham

Concepto:
Consulting Services - June 2025
Cantidad: 10 horas
Precio unitario: $150.00

Subtotal: $1500.00
IVA: $120.00
Total: $1620.00

Output:
{{
  "invoice_number": "2025-07-0098",
  "date": "2025-07-01",
  "vendor": "Consulting Solutions LLC",
  "customer": "Omega Enterprises",
  "items": [
    {{
      "description": "Consulting Services - June 2025",
      "quantity": 10,
      "unit_price": 150.00,
      "total": 1500.00
    }}
  ],
  "subtotal": 1500.00,
  "tax": 120.00,
  "total_amount": 1620.00
}}

**Passage**:
{input}
"""
    )