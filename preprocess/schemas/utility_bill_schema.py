from pydantic import BaseModel, Field
from typing import List, Optional

def get_schema():
    return UtilityBillSchema

class UsageDetail(BaseModel):
    type: Optional[str] = Field(None, description="Type of utility (electricity, water, gas, etc.)")
    usage_amount: Optional[float] = Field(None, description="Amount of usage")
    unit: Optional[str] = Field(None, description="Unit of measurement (kWh, m³, etc.)")
    cost: Optional[float] = Field(None, description="Cost for this usage")

class BillingPeriod(BaseModel):
    start_date: Optional[str] = Field(None, description="Billing period start date")
    end_date: Optional[str] = Field(None, description="Billing period end date")

class UtilityBillSchema(BaseModel):
    customer_name: Optional[str] = Field(None, description="Customer's name")
    account_number: Optional[str] = Field(None, description="Account number")
    address: Optional[str] = Field(None, description="Service address")
    provider_name: Optional[str] = Field(None, description="Utility provider name")
    billing_period: Optional[BillingPeriod] = None
    issue_date: Optional[str] = Field(None, description="Date bill was issued")
    due_date: Optional[str] = Field(None, description="Due date for payment")
    total_amount_due: Optional[float] = Field(None, description="Total amount due")
    usage_details: Optional[List[UsageDetail]] = Field(default_factory=list, description="Usage details")

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
  "customer_name": str or null,
  "account_number": str or null,
  "address": str or null,
  "provider_name": str or null,
  "billing_period": {"start_date": str or null, "end_date": str or null},
  "issue_date": str or null,
  "due_date": str or null,
  "total_amount_due": float or null,
  "usage_details": [
    {
      "type": str or null,
      "usage_amount": float or null,
      "unit": str or null,
      "cost": float or null
    }
  ]
}

Passage:
{{input}}
"""
    )
