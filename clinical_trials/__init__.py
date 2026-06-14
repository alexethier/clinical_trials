"""
Clinical Trials API Package
A Python library for searching and retrieving clinical trial data from ClinicalTrials.gov
"""

__version__ = "0.1.0"
__author__ = "Clinical Trials Research Tool"

from .api.client import ClinicalTrialsClient
from .models.study import Study, StudyStatus, StudyPhase
from .models.search import SearchParams, SearchResult

__all__ = [
    "ClinicalTrialsClient",
    "Study", 
    "StudyStatus",
    "StudyPhase",
    "SearchParams",
    "SearchResult"
]