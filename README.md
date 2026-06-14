# Clinical Trials Search Tool

A Python library and CLI tool for searching and retrieving clinical trial data from ClinicalTrials.gov.

## Features

- **Object-oriented design** with clean separation of concerns
- **Rich CLI interface** with multiple output formats
- **Comprehensive search capabilities** by condition, intervention, sponsor, phase, status
- **Export options** to JSON, CSV formats
- **Beautiful terminal output** using Rich library
- **Type hints** for better development experience

## Installation

```bash
poetry install
```

## Usage

### CLI Interface

Search for clinical trials:
```bash
poetry run clinical-trials search --condition "Hodgkin Lymphoma" --recruiting --max-studies 20
```

Get study details:
```bash
poetry run clinical-trials study NCT05675410
```

### Python API

```python
from clinical_trials import ClinicalTrialsClient, SearchParams

client = ClinicalTrialsClient()
params = SearchParams(condition="Hodgkin Lymphoma", recruiting_only=True)
results = client.search(params)

for study in results.studies:
    print(f"{study.nct_id}: {study.brief_title}")
```

## Architecture

- `models/` - Data models for studies, search parameters, and results
- `api/` - API client for ClinicalTrials.gov
- `cli/` - Command-line interface
- `utils/` - Utility functions and formatters