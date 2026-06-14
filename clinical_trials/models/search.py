"""Search models for clinical trials queries"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from .study import Study, StudyStatus, StudyPhase


class SortOrder(Enum):
    """Sort order options"""
    ASC = "asc"
    DESC = "desc"


class SortBy(Enum):
    """Sort field options"""
    STUDY_FIRST_POSTED_DATE = "StudyFirstPostedDate"
    LAST_UPDATE_POSTED_DATE = "LastUpdatePostedDate"
    NCT_ID = "NCTId"
    ENROLLMENT = "EnrollmentCount"
    START_DATE = "StartDate"


@dataclass
class SearchParams:
    """Parameters for clinical trials search"""
    condition: Optional[str] = None
    intervention: Optional[str] = None
    sponsor: Optional[str] = None
    status: Optional[StudyStatus] = None
    phase: Optional[StudyPhase] = None
    country: Optional[str] = None
    city: Optional[str] = None
    study_type: Optional[str] = None
    primary_purpose: Optional[str] = None
    recruiting_only: bool = False
    max_studies: int = 10
    sort_by: SortBy = SortBy.LAST_UPDATE_POSTED_DATE
    sort_order: SortOrder = SortOrder.DESC
    fields: Optional[List[str]] = None
    
    def __post_init__(self):
        """Set default fields if not provided"""
        if self.fields is None:
            self.fields = [
                "NCTId", "BriefTitle", "OfficialTitle", "OverallStatus",
                "Phase", "StudyType", "Condition", "InterventionName",
                "PrimaryPurpose", "BriefSummary", "DetailedDescription",
                "StartDate", "CompletionDate", "EnrollmentCount",
                "LocationCity", "LocationCountry", "Sponsor",
                "StudyFirstPostedDate", "LastUpdatePostedDate"
            ]
    
    def to_search_expression(self) -> str:
        """Convert parameters to ClinicalTrials.gov search expression"""
        expressions = []
        
        if self.condition:
            expressions.append(f"AREA[Condition]{self.condition}")
        
        if self.intervention:
            expressions.append(f"AREA[InterventionName]{self.intervention}")
        
        if self.sponsor:
            expressions.append(f"AREA[Sponsor]{self.sponsor}")
        
        if self.status:
            expressions.append(f"AREA[OverallStatus]{self.status.value}")
        
        if self.phase:
            expressions.append(f"AREA[Phase]{self.phase.value}")
        
        if self.country:
            expressions.append(f"AREA[LocationCountry]{self.country}")
        
        if self.city:
            expressions.append(f"AREA[LocationCity]{self.city}")
        
        if self.study_type:
            expressions.append(f"AREA[StudyType]{self.study_type}")
        
        if self.primary_purpose:
            expressions.append(f"AREA[PrimaryPurpose]{self.primary_purpose}")
        
        if self.recruiting_only:
            recruiting_statuses = [
                StudyStatus.RECRUITING.value,
                StudyStatus.NOT_YET_RECRUITING.value
            ]
            status_expr = " OR ".join([f'AREA[OverallStatus]"{status}"' for status in recruiting_statuses])
            expressions.append(f"({status_expr})")
        
        return " AND ".join(expressions) if expressions else ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls"""
        return {
            "search_expr": self.to_search_expression(),
            "fields": self.fields,
            "max_studies": self.max_studies,
            "fmt": "json"
        }


@dataclass
class SearchResult:
    """Result of a clinical trials search"""
    studies: List[Study] = field(default_factory=list)
    total_count: int = 0
    search_params: Optional[SearchParams] = None
    api_info: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_api_response(cls, response_data: Dict[str, Any], search_params: SearchParams) -> "SearchResult":
        """Create SearchResult from API response"""
        studies = []
        total_count = 0
        
        if "studies" in response_data:
            study_data_list = response_data["studies"]
            total_count = len(study_data_list)
            
            for study_data in study_data_list:
                try:
                    study = Study.from_api_data(study_data)
                    studies.append(study)
                except Exception as e:
                    print(f"Warning: Failed to parse study data: {e}")
                    continue
        
        return cls(
            studies=studies,
            total_count=total_count,
            search_params=search_params,
            api_info=response_data.get("api_info")
        )
    
    def filter_by_status(self, status: StudyStatus) -> "SearchResult":
        """Filter results by study status"""
        filtered_studies = [s for s in self.studies if s.overall_status == status]
        return SearchResult(
            studies=filtered_studies,
            total_count=len(filtered_studies),
            search_params=self.search_params
        )
    
    def filter_recruiting(self) -> "SearchResult":
        """Filter for recruiting studies only"""
        filtered_studies = [s for s in self.studies if s.is_recruiting]
        return SearchResult(
            studies=filtered_studies,
            total_count=len(filtered_studies),
            search_params=self.search_params
        )
    
    def get_by_nct_id(self, nct_id: str) -> Optional[Study]:
        """Get study by NCT ID"""
        for study in self.studies:
            if study.nct_id == nct_id:
                return study
        return None
    
    def group_by_status(self) -> Dict[StudyStatus, List[Study]]:
        """Group studies by status"""
        groups: Dict[StudyStatus, List[Study]] = {}
        for study in self.studies:
            if study.overall_status:
                if study.overall_status not in groups:
                    groups[study.overall_status] = []
                groups[study.overall_status].append(study)
        return groups
    
    def group_by_phase(self) -> Dict[StudyPhase, List[Study]]:
        """Group studies by phase"""
        groups: Dict[StudyPhase, List[Study]] = {}
        for study in self.studies:
            if study.phase:
                if study.phase not in groups:
                    groups[study.phase] = []
                groups[study.phase].append(study)
        return groups
    
    def __len__(self) -> int:
        return len(self.studies)
    
    def __iter__(self):
        return iter(self.studies)