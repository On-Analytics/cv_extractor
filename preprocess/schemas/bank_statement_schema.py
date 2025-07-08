from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

def get_schema():
    return BankStatementSchema

class Transaction(BaseModel):
    date: Optional[str] = Field(None, description="Date of transaction formatted as 'YYYY-MM-DD'")
    description: Optional[str] = Field(None, description="Description of transaction")
    amount: Optional[float] = Field(None, description="Amount of transaction")
    balance: Optional[float] = Field(None, description="Balance after transaction")
    transaction_type: Optional[str] = Field(None, description="Type of transaction (debit/credit)")

class StatementPeriod(BaseModel):
    start_date: Optional[str] = Field(None, description="Statement period start date formatted as 'YYYY-MM-DD'")
    end_date: Optional[str] = Field(None, description="Statement period end date formatted as 'YYYY-MM-DD'")

class BankStatementSchema(BaseModel):
    account_holder_name: Optional[str] = Field(None, description="Name of account holder")
    account_number: Optional[str] = Field(None, description="Account number")
    bank_name: Optional[str] = Field(None, description="Name of the bank")
    statement_period: Optional[StatementPeriod] = None
    opening_balance: Optional[float] = Field(None, description="Opening balance")
    closing_balance: Optional[float] = Field(None, description="Closing balance")
    currency: Optional[str] = Field(None, description="Currency type")
    transactions: Optional[List[Transaction]] = Field(default_factory=list, description="List of transactions")

    @field_validator('transactions', mode='before')
    def empty_list_if_none(cls, v):
        """If 'transactions' is None, convert it to an empty list before validation."""
        if v is None:
            return []
        return v



def get_prompt():
    return (
        """
Follow these instructions:

- DO NOT extract or include any other fields.
- Do NOT guess or infer values.
- Do NOT use placeholders like 'N/A', 'Not specified', etc.
- Output must be a valid JSON object with ONLY the fields above (even if all are null or empty arrays).

Passage:
{{input}}
"""
    )
