"""Clinical trials API client"""

from typing import Optional, List, Dict, Any
import logging
from .direct_client import DirectClinicalTrialsClient, ClinicalTrialsAPIError
from ..models.study import Study
from ..models.search import SearchParams, SearchResult


logger = logging.getLogger(__name__)


class ClinicalTrialsClient:
    """Main client for interacting with ClinicalTrials.gov API"""
    
    def __init__(self):
        """Initialize the client"""
        self._client = DirectClinicalTrialsClient()
        logger.info("ClinicalTrialsClient initialized")
    
    def search(self, search_params: SearchParams) -> SearchResult:
        """
        Search for clinical trials
        
        Args:
            search_params: Search parameters object
            
        Returns:
            SearchResult containing matched studies
        """
        return self._client.search(search_params)
    
    def search_by_condition(
        self,
        condition: str,
        recruiting_only: bool = False,
        max_studies: int = 10
    ) -> SearchResult:
        """
        Simple search by medical condition
        
        Args:
            condition: Medical condition to search for
            recruiting_only: Filter for recruiting studies only
            max_studies: Maximum number of studies to return
            
        Returns:
            SearchResult containing matched studies
        """
        return self._client.search_by_condition(condition, recruiting_only, max_studies)
    
    def get_study(self, nct_id: str) -> Optional[Study]:
        """
        Get a specific study by NCT ID
        
        Args:
            nct_id: NCT ID of the study
            
        Returns:
            Study object or None if not found
        """
        return self._client.get_study(nct_id)
    
    def get_full_study(self, nct_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full study details by NCT ID
        
        Args:
            nct_id: NCT ID of the study
            
        Returns:
            Full study data dictionary or None if not found
        """
        study = self._client.get_study(nct_id)
        return study.raw_data if study else None
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Get API information including version and last update
        
        Returns:
            API information dictionary
        """
        return {
            "api_version": "v2",
            "base_url": "https://clinicaltrials.gov/api/v2/studies",
            "client": "DirectClinicalTrialsClient"
        }
    
    def get_available_fields(self) -> List[str]:
        """
        Get list of available study fields
        
        Returns:
            List of field names
        """
        return [
            "nctId", "briefTitle", "officialTitle", "overallStatus",
            "phase", "studyType", "condition", "interventionName",
            "primaryPurpose", "briefSummary", "detailedDescription",
            "startDate", "completionDate", "enrollment",
            "locationCity", "locationCountry", "sponsor"
        ]