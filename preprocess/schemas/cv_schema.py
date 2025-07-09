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
    year: Optional[str] = Field(None, description="Year of graduation or attendance period formatted as 'YYYY', if present")
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
    start_date: Optional[str] = Field(None, description="Start date of the position formatted as 'YYYY-MM-DD' or 'YYYY', if present")
    end_date: Optional[str] = Field(None, description="End date of the position formatted as 'YYYY-MM-DD', 'YYYY' or 'Present/Current', if present")
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
    education: Optional[List[Education]] = Field(default_factory=list,description="List of educational qualifications in reverse chronological order. Sometimes educations comes under the name of formation or studies")
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
Follow these instructions:

- List all professional experience, for each professional experience extract the start_date and end_date as a year if present (e.g., '2005', '2007', 'Present').
- Do NOT guess or infer values that are not present in the document.
- Do NOT use placeholders like 'N/A', 'Not specified', 'City', 'Company Name', etc.
- Output must be a valid JSON object with ONLY the fields above (even if all except summary are null or empty arrays).


**Examples**:
Example 1:
Passage:
John Doe
Email: john.doe@email.com
Phone: +1 555-1234
Location: New York, USA
LinkedIn: linkedin.com/in/johndoe

Professional Experience:
Software Engineer at Acme Corp (2018 - 2021)
- Developed web applications using Python and Django.
- Led a team of 4 engineers.

Education:
BSc Computer Science, MIT, 2017

Skills: Python, Django, Leadership
Languages: English (Native), Spanish (Fluent)

Output:
{{
  "summary": "Software engineer with experience in web application development and team leadership. Skilled in Python and Django.",
  "name": "John Doe",
  "location": {{"city": "New York", "country": "USA", "region": null}},
  "email": "john.doe@email.com",
  "phone": "+1 555-1234",
  "profiles": [{{"network": "LinkedIn", "url": "linkedin.com/in/johndoe"}}],
  "professional_experience": [
    {{
      "position": "Software Engineer",
      "company": "Acme Corp",
      "start_date": "2018",
      "end_date": "2021",
      "description": "Developed web applications using Python and Django. Led a team of 4 engineers."
    }}
  ],
  "education": [
    {{
      "degree": "BSc Computer Science",
      "institution": "MIT",
      "year": "2017",
      "field": null
    }}
  ],
  "skills": ["Python", "Django", "Leadership"],
  "languages": [
    {{"language": "English", "proficiency": "Native"}},
    {{"language": "Spanish", "proficiency": "Fluent"}}
  ],
  "certifications": []
}}

Example 2:
Passage:
Maria Rossi
Email: maria.rossi@email.it
Location: Milan, Italy

Professional Experience:
Marketing Specialist, Beta S.p.A. (2020 - Present)
- Managed digital marketing campaigns.

Education:
Laurea in Economia, Università di Milano, 2019

Skills: SEO, Google Analytics
Languages: Italian (Native), English (Intermediate)

Output:
{{
  "summary": "Marketing specialist with experience in digital campaigns. Skilled in SEO and Google Analytics.",
  "name": "Maria Rossi",
  "location": {{"city": "Milan", "country": "Italy", "region": null}},
  "email": "maria.rossi@email.it",
  "phone": null,
  "profiles": [],
  "professional_experience": [
    {{
      "position": "Marketing Specialist",
      "company": "Beta S.p.A.",
      "start_date": "2020",
      "end_date": "Present",
      "description": "Managed digital marketing campaigns."
    }}
  ],
  "education": [
    {{
      "degree": "Laurea in Economia",
      "institution": "Università di Milano",
      "year": "2019",
      "field": null
    }}
  ],
  "skills": ["SEO", "Google Analytics"],
  "languages": [
    {{"language": "Italian", "proficiency": "Native"}},
    {{"language": "English", "proficiency": "Intermediate"}}
  ],
  "certifications": []
}}

Passage:
{input}
"""
    )
