#!/bin/bash
# Clinical Trials Search Script for Lymphoma
# Usage: ./search.sh "search_text" [limit] [format]

# Check if help is requested or no args provided
if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Usage: $0 \"search_text\" [limit] [format]"
    echo "Search for lymphoma clinical trials with recruiting status"
    echo ""
    echo "Arguments:"
    echo "  search_text    Search term (required)"
    echo "  limit         Maximum studies to return (optional, default: 10)"
    echo "  format        Output format: list|table|summary|json|csv|yaml (optional, default: list)"
    echo ""
    echo "Examples:"
    echo "  $0 \"Hodgkin\" 10"
    echo "  $0 \"immunotherapy\" 5 json"
    echo "  $0 \"brentuximab\" 10 table"
    exit 0
fi

SEARCH_TEXT="$1"
LIMIT="${2:-10}"  # Default to 10 if not provided
FORMAT="${3:-list}"  # Default to list if not provided
CONDITION="Lymphoma"  # Hardcoded to Lymphoma

# Only show debug info for non-json/yaml formats
if [ "$FORMAT" != "json" ] && [ "$FORMAT" != "yaml" ]; then
    echo "Searching for: $SEARCH_TEXT"
    echo "Condition filter: $CONDITION"
    echo "Limit: $LIMIT studies"
    echo "Format: $FORMAT"
    echo "---"
    
    # Build and echo the command
    CMD="poetry run clinical-trials search --search-text \"$SEARCH_TEXT\" --condition \"$CONDITION\" --recruiting --max-studies $LIMIT --format $FORMAT"
    echo "Running: $CMD"
    echo ""
    
    # Execute the command
    eval $CMD
else
    # For JSON/YAML, output only the data
    poetry run clinical-trials search --search-text "$SEARCH_TEXT" --condition "$CONDITION" --recruiting --max-studies $LIMIT --format $FORMAT
fi