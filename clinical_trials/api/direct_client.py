"""Direct API client for ClinicalTrials.gov without pytrials dependency"""

import requests
import logging
from typing import Optional, List, Dict, Any
from ..models.study import Study
from ..models.search import SearchParams, SearchResult


logger = logging.getLogger(__name__)


class DirectClinicalTrialsClient:
    """Direct client for ClinicalTrials.gov API v2"""
    
    def __init__(self):
        """Initialize the direct client"""
        self.base_url = "https://clinicaltrials.gov/api/v2/studies"
        self.session = requests.Session()
        logger.info("DirectClinicalTrialsClient initialized")
    
    def search(self, search_params: SearchParams) -> SearchResult:
        """
        Search for clinical trials using direct API
        
        Args:
            search_params: Search parameters object
            
        Returns:
            SearchResult containing matched studies
        """
        try:
            logger.info(f"Searching with params: {search_params}")
            
            # Build API parameters
            params = self._build_api_params(search_params)
            
            # Make API call
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Convert response to SearchResult
            result = self._parse_response(data, search_params)
            
            logger.info(f"Search completed. Found {result.total_count} studies")
            return result
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise ClinicalTrialsAPIError(f"Search failed: {e}") from e
    
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
        search_params = SearchParams(
            condition=condition,
            recruiting_only=recruiting_only,
            max_studies=max_studies
        )
        return self.search(search_params)
    
    def get_study(self, nct_id: str) -> Optional[Study]:
        """
        Get a specific study by NCT ID
        
        Args:
            nct_id: NCT ID of the study
            
        Returns:
            Study object or None if not found
        """
        try:
            url = f"{self.base_url}/{nct_id}"
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            if "studies" in data and data["studies"]:
                study_data = self._extract_study_fields(data["studies"][0])
                return Study.from_api_data(study_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get study {nct_id}: {e}")
            if "404" in str(e):
                return None
            raise ClinicalTrialsAPIError(f"Failed to get study {nct_id}: {e}") from e
    
    def _build_api_params(self, search_params: SearchParams) -> Dict[str, Any]:
        """Build API parameters from search params"""
        params = {
            "format": "json",
            "pageSize": search_params.max_studies
        }
        
        # Add general search text
        if search_params.search_text:
            params["query.term"] = search_params.search_text
        
        # Add search filters
        if search_params.condition:
            params["query.cond"] = search_params.condition
        
        if search_params.intervention:
            params["query.intr"] = search_params.intervention
        
        if search_params.sponsor:
            params["query.spons"] = search_params.sponsor
        
        if search_params.country:
            params["filter.geo"] = search_params.country
        
        if search_params.recruiting_only or search_params.status:
            if search_params.recruiting_only:
                params["filter.overallStatus"] = "RECRUITING"
            elif search_params.status:
                params["filter.overallStatus"] = search_params.status.value.upper().replace(" ", "_")
        
        if search_params.phase:
            phase_mapping = {
                "Early Phase 1": "EARLY_PHASE1",
                "Phase 1": "PHASE1",
                "Phase 1/Phase 2": "PHASE1_PHASE2",
                "Phase 2": "PHASE2",
                "Phase 2/Phase 3": "PHASE2_PHASE3",
                "Phase 3": "PHASE3",
                "Phase 4": "PHASE4",
                "Not Applicable": "NA"
            }
            if search_params.phase.value in phase_mapping:
                params["filter.phase"] = phase_mapping[search_params.phase.value]
        
        return params
    
    def _parse_response(self, data: Dict[str, Any], search_params: SearchParams) -> SearchResult:
        """Parse API response into SearchResult"""
        studies = []
        
        if "studies" in data:
            for study_data in data["studies"]:
                try:
                    # Extract fields from the new API format
                    extracted_data = self._extract_study_fields(study_data)
                    study = Study.from_api_data(extracted_data)
                    studies.append(study)
                except Exception as e:
                    logger.warning(f"Failed to parse study: {e}")
                    continue
        
        return SearchResult(
            studies=studies,
            total_count=len(studies),
            search_params=search_params
        )
    
    def _extract_study_fields(self, study_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and map fields from new API format to old format"""
        protocol_section = study_data.get("protocolSection", {})
        
        # Identification
        identification = protocol_section.get("identificationModule", {})
        
        # Status
        status_module = protocol_section.get("statusModule", {})
        
        # Design
        design_module = protocol_section.get("designModule", {})
        
        # Description
        description_module = protocol_section.get("descriptionModule", {})
        
        # Conditions
        conditions_module = protocol_section.get("conditionsModule", {})
        
        # Interventions
        interventions_module = protocol_section.get("armsInterventionsModule", {})
        
        # Contacts and locations
        contacts_module = protocol_section.get("contactsLocationsModule", {})
        
        # Sponsors
        sponsors_module = protocol_section.get("sponsorCollaboratorsModule", {})
        
        # Eligibility
        eligibility_module = protocol_section.get("eligibilityModule", {})
        
        # Map to old format
        extracted = {
            "nctId": identification.get("nctId"),
            "briefTitle": identification.get("briefTitle"),
            "officialTitle": identification.get("officialTitle"),
            "overallStatus": status_module.get("overallStatus"),
            "phase": design_module.get("phases", [None])[0] if design_module.get("phases") else None,
            "studyType": design_module.get("studyType"),
            "primaryPurpose": design_module.get("designInfo", {}).get("primaryPurpose"),
            "briefSummary": description_module.get("briefSummary"),
            "detailedDescription": description_module.get("detailedDescription"),
            "condition": conditions_module.get("conditions", []),
            "interventionName": [],
            "startDate": status_module.get("startDateStruct", {}).get("date"),
            "completionDate": status_module.get("primaryCompletionDateStruct", {}).get("date"),
            "enrollment": design_module.get("enrollmentInfo", {}).get("count"),
            "locations": {},
            "sponsor": []
        }
        
        # Extract interventions
        if interventions_module.get("interventions"):
            extracted["interventionName"] = [
                interv.get("name", "") for interv in interventions_module["interventions"]
            ]
        
        # Extract locations (grouped by country)
        if contacts_module.get("locations"):
            locations_by_country = {}
            for location in contacts_module["locations"]:
                country = location.get("country", "Unknown")
                city = location.get("city")
                if city:
                    if country not in locations_by_country:
                        locations_by_country[country] = set()
                    locations_by_country[country].add(city)
            
            # Convert to final format with cities under countries
            extracted["locations"] = {
                country: list(cities) for country, cities in locations_by_country.items()
            }
        
        # Extract sponsors
        if sponsors_module.get("leadSponsor"):
            extracted["sponsor"] = [sponsors_module["leadSponsor"].get("name", "")]
        
        return extracted


class ClinicalTrialsAPIError(Exception):
    """Custom exception for API errors"""
    pass