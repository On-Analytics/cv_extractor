from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

def get_schema():
    return UtilityBillSchema

class UsageDetail(BaseModel):
    type: Optional[str] = Field(None, description="Type of utility (electricity, water, gas, etc.)")
    usage_amount: Optional[float] = Field(None, description="Amount of usage")
    unit: Optional[str] = Field(None, description="Unit of measurement (kWh, m³, etc.)")
    cost: Optional[float] = Field(None, description="Cost for this usage")

class BillingPeriod(BaseModel):
    start_date: Optional[str] = Field(None, description="Billing period start date formatted as 'YYYY-MM-DD'")
    end_date: Optional[str] = Field(None, description="Billing period end date formatted as 'YYYY-MM-DD'")

class UtilityBillSchema(BaseModel):
    customer_name: Optional[str] = Field(None, description="Customer's name")
    account_number: Optional[str] = Field(None, description="Account number")
    address: Optional[str] = Field(None, description="Service address")
    provider_name: Optional[str] = Field(None, description="Utility provider name")
    billing_period: Optional[BillingPeriod] = None
    issue_date: Optional[str] = Field(None, description="Date bill was issued formatted as 'YYYY-MM-DD'")
    due_date: Optional[str] = Field(None, description="Due date for payment formatted as 'YYYY-MM-DD'")
    total_amount_due: Optional[float] = Field(None, description="Total amount due")
    usage_details: Optional[List[UsageDetail]] = Field(default_factory=list, description="Usage details")

    @field_validator('usage_details', mode='before')
    def empty_list_if_none(cls, v):
        """If 'usage_details' is None, convert it to an empty list before validation."""
        if v is None:
            return []
        return v



def get_prompt():
    return (
        """
Follow these instructions:

- Do NOT guess or infer values that are not present in the document.
- Do NOT use placeholders like 'N/A', 'Not specified', etc.
- Output must be a valid JSON object with ONLY the fields above (even if all are null or empty arrays).

Passage:
{input}
"""
    )
