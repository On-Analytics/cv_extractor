from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
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
    language: str = Field(..., description="Name of the language")
    proficiency: Optional[str] = Field(None, description="Proficiency level (e.g., Native, Fluent, Intermediate, Basic)")

class Profile(BaseModel):
    """Social media or professional network profile information."""
    network: str = Field(..., description="Name of the social network or platform (e.g., LinkedIn, GitHub)")
    url: str = Field(..., description="URL to the candidate's profile")

class Experience(BaseModel):
    """Professional experience information.
    - start_date: Start date of the position (e.g., "Aug 2005")
    - end_date: End date of the position (e.g., "Aug 2007" or "Present")
    """
    position: Optional[str] = Field(None, description="Job title/position")
    company: Optional[str] = Field(None, description="Name of the company")
    start_date: Optional[str] = Field(None, description="Start date of the position (e.g., 'Aug 2005')")
    end_date: Optional[str] = Field(None, description="End date of the position (e.g., 'Aug 2007' or 'Present/Current')")
    description: Optional[str] = Field(None, description="Additional details about the role or responsibilities")

class DocumentSchema(BaseModel):
    """Structured schema for document data extraction."""
    summary: str = Field(
        ...,
        description=("High level summary of the document with relevant roles and experience. Include all relevant information to provide full picture."
        "Do no use any pronouns"),
    )
    name: Optional[str] = Field(None, description="Full name of the candidate")
    location: Optional[Location] = Field(None, description="Geographic location details")
    email: Optional[str] = Field(None, description="Primary email address for contact")
    phone: Optional[str] = Field(None, description="Contact phone number with country code")
    profiles: List[Profile] = Field(
        default_factory=list,
        description="List of social media and professional network profiles"
    )
    professional_experience: List[Experience] = Field(
        default_factory=list,
        description="List of professional experience entries"
    )
    education: List[Education] = Field(
        default_factory=list,
        description="List of educational qualifications in reverse chronological order"
    )
    skills: List[str] = Field(
        default_factory=list,
        description="List of professional skills and competencies"
    )
    languages: List[Language] = Field(
        default_factory=list,
        description="List of languages spoken and proficiency levels"
    )
    certifications: List[str] = Field(
        default_factory=list,
        description="List of professional certifications and qualifications"
    )

