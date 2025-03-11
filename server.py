from mcp.server.fastmcp import FastMCP
import requests
import json
from typing import Optional, Dict, Any, List, Union

mcp = FastMCP("BioStudies")

def _make_api_request(url: str, params: Dict = None) -> str:
    """Helper function to make API requests and handle responses"""
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        else:
            return f"Error: Request failed with status code {response.status_code}. Response: {response.text}"
    
    except Exception as e:
        return f"Error: An exception occurred during request: {str(e)}"

@mcp.tool()
def get_study(accession: str) -> str:
    """Get a study from the BioStudies database with the given accession"""
    url = f"https://www.ebi.ac.uk/biostudies/api/v1/studies/{accession}"
    return _make_api_request(url)

@mcp.tool()
def search_studies(params: str) -> str:
    """
    Search for studies in the BioStudies database.
    
    Parameters:
    - params: A string containing all search parameters in the format "param1=value1&param2=value2"
      
    Supported parameters include:
    - query: Searches for the provided text in all submissions
      * Each word is treated as a separate term unless in double quotes
      * Boolean operators (AND, OR, NOT) and brackets can modify behavior: e.g., "Leukemia AND (mouse OR human)"
      * Wildcards: * matches any sequence of characters, ? matches any single character
      * Regular expressions supported using /pattern/ syntax
      * Special characters (+, -, &&, ||, !, (), {}, [], ^, \", ~, *, ?, :, \\, /) need to be escaped or quoted
      * DOIs and paths should be in quotes: e.g., "10.1371/journal.pone.0127346" or "eeg/fmri"
    - accession: Searches for a specific BioStudies accession (wildcards allowed after first character, e.g. S-EPMC*)
    - title: Searches for presence of the parameter in the title of the study
    - author: Searches for presence of the parameter in the name of the author(s)/submitter(s)
    - release_date: Searches for a specific release date (format: yyyy-mm-dd) Wildcards and ranges supported. For example: 2009* will search for experiments released in 2009 and [2008-01-01 2008-05-31] will search for experiments released between 1st of Jan and end of May 2008. 
    - content: Free-text search in any part of the study content (including file names and links)
    - links: Number of links in the study
    - files: Number of files in the study
    - orcid: Searches for the ORCID of any authors of the study (if available)
    - type: Study type (supported: 'study', 'array', 'collection')
    - link_type: Searches for a specific type of link to external databases
    - link_value: Searches in the value of the link type field
    - page: Result page number (default: 1)
    - pageSize: Number of results per page (default: 20, max: 100)
    - sortBy: Sorting key (works only for numeric fields)
    - sortOrder: Sorting order ('ascending' or 'descending', default: 'descending')
    - collection: Optional collection name to limit search to a specific collection
    
    Collection-specific fields can also be used depending on the collection:
    
    For ArrayExpress collection, functional genomics experiments data:
    - experimental_design: Experiment design
    - study_type: Study type
    - experimental_factor: Experimental factor
    - experimental_factor_value: The value of an experimental factor
    - source_characteristics: Sample attribute values / Source Characteristics 
    - source_characteristics_value: Sample attribute category / Source Characteristics value
    - technology: Technology    
    - organism: Species/organism of the experiment, study or sample
    - gxa: Presence ("true") / absence ("false") in Expression Atlas
    - raw: Experiment has raw data available
    - processed: Experiment has processed data available
    - assay_count: The number of of assays
    - sample_count: The number of samples
    - experimental_factor_count: The number of experimental factors
    - miame_score: The MIAME compliance score
    - minseqe_score: The MINSEQE compliance score

    For BioModels collection:
    - domain: Domain of the model
    - curation_status: Curation status of the model
    - modelling_approach: Modeling approach used
    - model_format: Format of the model
    - model_tags: Tags associated with the model
    - organism: Organism in the model
    
    Returns:
    - JSON string with search results
    """
    # Parse the query parameters
    param_dict = {}
    if params:
        param_pairs = params.split('&')
        for pair in param_pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                param_dict[key] = value
    
    # Extract collection if present
    collection = param_dict.pop('collection', None)
    
    # Determine the base URL based on whether a collection is specified
    base_url = f"https://www.ebi.ac.uk/biostudies/api/v1/{collection}/search" if collection else "https://www.ebi.ac.uk/biostudies/api/v1/search"
    
    # Filter out facet.* parameters
    param_dict = {k: v for k, v in param_dict.items() if not k.startswith("facet.")}
    
    # Set default pagination parameters if not provided
    if 'page' not in param_dict:
        param_dict['page'] = '1'
    if 'pageSize' not in param_dict:
        param_dict['pageSize'] = '20'
    if 'sortOrder' not in param_dict:
        param_dict['sortOrder'] = 'descending'
    
    return _make_api_request(base_url, param_dict)

@mcp.tool()
def get_study_info(accession: str) -> str:
    """
    Get additional information for a study with the given accession.
    
    Returns information such as FTP link and relative path.
    
    Parameters:
    - accession: The BioStudies accession ID
    
    Returns:
    - JSON string with additional study information
    """
    url = f"https://www.ebi.ac.uk/biostudies/api/v1/studies/{accession}/info"
    return _make_api_request(url)
