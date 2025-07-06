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

class Location(BaseModel):
    """Geographic location information."""
    city: Optional[str] = Field(None, description="Name of the city where the candidate is located")
    country: Optional[str] = Field(None, description="Name of the country where the candidate is located")
    region: Optional[str] = Field(None, description="State, province, or region within the country")

class Education(BaseModel):
    """Educational background information."""
    degree: Optional[str] = Field(None, description="Academic degree earned (e.g., Bachelor's, Master's, PhD)")
    institution: str = Field(..., description="Name of the educational institution")
    year: Optional[str] = Field(None, description="Year of graduation or attendance period")
    field: Optional[str] = Field(None, description="Field of study or major")

class Language(BaseModel):
    """Language proficiency information."""
    language: Optional[str] = Field(None, description="Name of the language")
    proficiency: Optional[str] = Field(None, description="Proficiency level (e.g., Native, Fluent, Intermediate, Basic)")

class Profile(BaseModel):
    """Social media or professional network profile information."""
    network: Optional[str] = Field(None, description="Name of the social network or platform (e.g., LinkedIn, GitHub)")
    url: Optional[str] = Field(None, description="URL to the candidate's profile")

class Experience(BaseModel):
    """Professional experience information.
    - start_date: Start date of the position (e.g., "Aug 2005")
    - end_date: End date of the position (e.g., "Aug 2007" or "Present")
    """
    position: Optional[str] = Field(None, description="Job title/position")
    company: Optional[str] = Field(None, description="Name of the company")
    start_date: Optional[str] = Field(None, description="Start date of the position (e.g., '2005')")
    end_date: Optional[str] = Field(None, description="End date of the position (e.g., '2007' or 'Present/Current')")
    description: str = Field(..., description="Additional details about the role or responsibilities")


class DocumentSchema(BaseModel):
    """Structured schema for document data extraction."""
    summary: str = Field(
        ...,
        description=("High level summary of the document with relevant roles and experience. Include all relevant information to provide full picture."
        "Do no use any pronouns"),
    )
    name: str = Field(..., description="Full name of the candidate")
    location: Optional[Location] = Field(None, description="Geographic location details")
    email: Optional[str] = Field(None, description="Primary email address for contact")
    phone: Optional[str] = Field(None, description="Contact phone number with country code")
    profiles: Optional[List[Profile]] = Field(default_factory=list, description="Social/professional profiles")
    professional_experience: Optional[List[Experience]] = Field(default_factory=list,description="List of professional experience entries")
    education: Optional[List[Education]] = Field(default_factory=list,description="List of educational qualifications in reverse chronological order")
    skills: Optional[List[str]] = Field(default_factory=list, description="List of skills")
    languages: Optional[List[Language]] = Field(default_factory=list, description="Languages spoken")
    certifications: Optional[List[str]] = Field(default_factory=list, description="Certifications obtained")

    @field_validator('profiles', 'professional_experience', 'education', 'skills', 'languages', 'certifications', mode='before')
    def empty_list_if_none(cls, v):
        """If a list field is None, convert it to an empty list before validation."""
        if v is None:
            return []
        return v

def get_schema():
    return DocumentSchema

def get_prompt():
    return (
        """

Extract ONLY the following fields as a JSON object with this structure and follow this instructions: 

- For each professional experience extract the start_date and end_date as a year if present (e.g., '2005', '2007', 'Present').
- DO NOT extract or include any other fields.
- Do NOT guess or infer values for fields not listed or values not present.
- Do NOT use placeholders like 'N/A', 'Not specified', 'City', 'Company Name', etc.
- Output must be a valid JSON object with ONLY the fields above (even if all except summary are null or empty arrays).

{{{{
  "summary": str,
  "name": str,
  "location": {{{{
    "city": str or null,
    "country": str or null,
    "region": str or null
  }}}},
  "email": str or null,
  "phone": str or null,
  "profiles": [str],
  "professional_experience": [
    {{{{
      "position": str or null,
      "company": str or null,
      "start_date": str or null,
      "end_date": str or null,
      "description": str
    }}}}
  ],
  "education": [
    {{{{
      "degree": str or null,
      "institution": str or null,
      "year": str or null,
      "field": str or null
    }}}}
  ],
  "skills": [str],
  "languages": [
    {{{{
      "language": str or null,
      "proficiency": str or null
    }}}}
  ],
  "certifications": [str]
}}}}

Passage:
{{input}}
"""
    )

