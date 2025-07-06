from pydantic import BaseModel, Field
from typing import List, Optional

def get_schema():
    return BankStatementSchema

class Transaction(BaseModel):
    date: Optional[str] = Field(None, description="Date of transaction")
    description: Optional[str] = Field(None, description="Description of transaction")
    amount: Optional[float] = Field(None, description="Amount of transaction")
    balance: Optional[float] = Field(None, description="Balance after transaction")
    transaction_type: Optional[str] = Field(None, description="Type of transaction (debit/credit)")

class StatementPeriod(BaseModel):
    start_date: Optional[str] = Field(None, description="Statement period start date")
    end_date: Optional[str] = Field(None, description="Statement period end date")

class BankStatementSchema(BaseModel):
    account_holder_name: Optional[str] = Field(None, description="Name of account holder")
    account_number: Optional[str] = Field(None, description="Account number")
    bank_name: Optional[str] = Field(None, description="Name of the bank")
    statement_period: Optional[StatementPeriod] = None
    opening_balance: Optional[float] = Field(None, description="Opening balance")
    closing_balance: Optional[float] = Field(None, description="Closing balance")
    currency: Optional[str] = Field(None, description="Currency type")
    transactions: Optional[List[Transaction]] = Field(default_factory=list, description="List of transactions")

def get_prompt():
    return (
        """
Follow these instructions:

- DO NOT extract or include any other fields.
- Do NOT guess or infer values.
- Do NOT use placeholders like 'N/A', 'Not specified', etc.
- Output must be a valid JSON object with ONLY the fields below (even if all are null or empty arrays).

Extract ONLY the following fields as a JSON object with this structure:
{
  "account_holder_name": str or null,
  "account_number": str or null,
  "bank_name": str or null,
  "statement_period": {"start_date": str or null, "end_date": str or null},
  "opening_balance": float or null,
  "closing_balance": float or null,
  "currency": str or null,
  "transactions": [
    {
      "date": str or null,
      "description": str or null,
      "amount": float or null,
      "balance": float or null,
      "transaction_type": str or null
    }
  ]
}

Passage:
{{input}}
"""
    )
