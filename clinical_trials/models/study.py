"""Study models for clinical trials data"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


class StudyStatus(Enum):
    """Clinical trial status enumeration"""
    NOT_YET_RECRUITING = "Not yet recruiting"
    RECRUITING = "Recruiting"
    ENROLLING_BY_INVITATION = "Enrolling by invitation"
    ACTIVE_NOT_RECRUITING = "Active, not recruiting"
    SUSPENDED = "Suspended"
    TERMINATED = "Terminated"
    COMPLETED = "Completed"
    WITHDRAWN = "Withdrawn"
    UNKNOWN = "Unknown status"


class StudyPhase(Enum):
    """Clinical trial phase enumeration"""
    EARLY_PHASE_1 = "Early Phase 1"
    PHASE_1 = "Phase 1"
    PHASE_1_2 = "Phase 1/Phase 2"
    PHASE_2 = "Phase 2"
    PHASE_2_3 = "Phase 2/Phase 3"
    PHASE_3 = "Phase 3"
    PHASE_4 = "Phase 4"
    NOT_APPLICABLE = "Not Applicable"


@dataclass
class Location:
    """Study location information"""
    facility: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    
    @property
    def full_address(self) -> str:
        """Get formatted full address"""
        parts = [self.facility, self.city, self.state, self.country]
        return ", ".join(filter(None, parts))


@dataclass
class Contact:
    """Study contact information"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


@dataclass
class Sponsor:
    """Study sponsor information"""
    name: Optional[str] = None
    agency_class: Optional[str] = None


@dataclass
class Study:
    """Clinical trial study model"""
    nct_id: str
    brief_title: str
    official_title: Optional[str] = None
    overall_status: Optional[StudyStatus] = None
    phase: Optional[StudyPhase] = None
    study_type: Optional[str] = None
    conditions: List[str] = field(default_factory=list)
    interventions: List[str] = field(default_factory=list)
    primary_purpose: Optional[str] = None
    detailed_description: Optional[str] = None
    brief_summary: Optional[str] = None
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    primary_completion_date: Optional[datetime] = None
    enrollment: Optional[int] = None
    locations: List[Location] = field(default_factory=list)
    sponsors: List[Sponsor] = field(default_factory=list)
    contacts: List[Contact] = field(default_factory=list)
    url: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Process data after initialization"""
        if self.nct_id:
            self.url = f"https://clinicaltrials.gov/study/{self.nct_id}"
    
    @classmethod
    def from_api_data(cls, data: Dict[str, Any]) -> "Study":
        """Create Study instance from API response data"""
        nct_id = data.get("nctId", "")
        brief_title = data.get("briefTitle", "")
        
        # Parse status
        status_str = data.get("overallStatus") or ""
        overall_status = None
        if status_str:
            for status in StudyStatus:
                if status.value.lower() == status_str.lower():
                    overall_status = status
                    break
        
        # Parse phase
        phase_str = data.get("phase") or ""
        phase = None
        if phase_str:
            for p in StudyPhase:
                if p.value.lower() == phase_str.lower():
                    phase = p
                    break
        
        # Parse conditions
        conditions = []
        if "condition" in data:
            if isinstance(data["condition"], list):
                conditions = data["condition"]
            else:
                conditions = [data["condition"]]
        
        # Parse locations
        locations = []
        if "locations" in data:
            locations_dict = data.get("locations", {})
            for country, cities in locations_dict.items():
                for city in cities:
                    locations.append(Location(city=city, country=country))
        elif "locationCity" in data:
            # Fallback for old format
            cities = data.get("locationCity", [])
            countries = data.get("locationCountry", [])
            if not isinstance(cities, list):
                cities = [cities]
            if not isinstance(countries, list):
                countries = [countries]
            
            for i, city in enumerate(cities):
                country = countries[i] if i < len(countries) else None
                locations.append(Location(city=city, country=country))
        
        # Parse sponsors
        sponsors = []
        if "sponsor" in data:
            sponsor_names = data["sponsor"]
            if not isinstance(sponsor_names, list):
                sponsor_names = [sponsor_names]
            for name in sponsor_names:
                sponsors.append(Sponsor(name=name))
        
        return cls(
            nct_id=nct_id,
            brief_title=brief_title,
            official_title=data.get("officialTitle"),
            overall_status=overall_status,
            phase=phase,
            study_type=data.get("studyType"),
            conditions=conditions,
            primary_purpose=data.get("primaryPurpose"),
            detailed_description=data.get("detailedDescription"),
            brief_summary=data.get("briefSummary"),
            enrollment=data.get("enrollment"),
            locations=locations,
            sponsors=sponsors,
            raw_data=data
        )
    
    @property
    def is_recruiting(self) -> bool:
        """Check if study is currently recruiting"""
        return self.overall_status in [StudyStatus.RECRUITING, StudyStatus.NOT_YET_RECRUITING]
    
    @property
    def primary_location(self) -> Optional[Location]:
        """Get primary study location"""
        return self.locations[0] if self.locations else None
    
    @property
    def primary_sponsor(self) -> Optional[Sponsor]:
        """Get primary sponsor"""
        return self.sponsors[0] if self.sponsors else None
    
    def __str__(self) -> str:
        return f"Study({self.nct_id}: {self.brief_title})"