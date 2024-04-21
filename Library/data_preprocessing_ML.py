import pandas as pd
import tldextract
import re
from urllib.parse import urlparse

def clean_extract_domain(url):
    """Cleans, standardizes URLs, and extracts the domain."""
    if pd.isna(url):
        return None
    url = re.sub(r'^(?:http:\/\/|https:\/\/)?(?:www\.)?', '', url)
    url = url.strip("/").strip()  # Clean trailing or leading slashes and spaces
    url = url.rstrip('/')
    try:
        parsed_url = urlparse('http://' + url)  # Ensure scheme is present for parsing
        domain = parsed_url.netloc
        domain = re.sub(r'^www\.', '', domain)  # Remove 'www.'
        return domain
    except Exception as e:
        print(f"Error parsing URL '{url}': {e}")
        return None

def extract_domain_features(domain):
    """Extracts various features from a domain."""
    if not domain:
        return {'domain_length': 0, 'unique_characters': 0, 'digit_count': 0,
                'letter_count': 0, 'hyphen_count': 0, 'dot_count': 0, 'exclamation_count': 0,
                'question_count': 0}
    extracted = tldextract.extract(domain)
    return {
        'domain_length': len(domain),
        'unique_characters': len(set(domain)),
        'digit_count': sum(c.isdigit() for c in domain),
        'letter_count': sum(c.isalpha() for c in domain),
        'hyphen_count': domain.count('-'),
        'dot_count': domain.count('.'),
        'exclamation_count': domain.count('!'),
        'question_count': domain.count('?')
    }

def load_data(dataset_query_path, search_results_paths):
    """
    Loads and merges the query dataset with multiple search results datasets.

    Parameters:
    - dataset_query_path: The file path to the dataset containing the queries and the correct URLs.
    - search_results_paths: A list of file paths to the datasets containing search results.

    Returns:
    - A merged DataFrame containing all the data.
    """
    # Load the dataset containing queries and correct URLs
    dataset_incl_query = pd.read_csv(dataset_query_path)
    dataset_incl_query.drop(columns=['Unnamed: 0'], inplace=True)  # Drop unnecessary columns

    # Initialize a DataFrame to hold the merged search results
    merged_search_results = pd.DataFrame()

    # Load and concatenate each search results dataset
    for path in search_results_paths:
        search_results = pd.read_csv(path)

        if merged_search_results.empty:
            merged_search_results = search_results
        else:
            # Ensure that the DataFrame structures align before concatenating
            merged_search_results = pd.concat([merged_search_results, search_results], axis=0, ignore_index=True)

    # Merge the query dataset with the concatenated search results
    merged_dataset = pd.merge(dataset_incl_query, merged_search_results, on='EntityNumber', how='left')

    return merged_dataset


def get_core_domain(url):
    """Extracts the core registrable domain from a URL using tldextract."""
    if pd.isna(url):
        return None
    try:
        extracted = tldextract.extract(url)
        if extracted.domain and extracted.suffix:  # Ensure domain and suffix are not empty
            return "{}.{}".format(extracted.domain, extracted.suffix).lower()
        return None
    except Exception as e:
        print(f"Error extracting domain from URL '{url}': {str(e)}")
        return None

def preprocess_domains(dataframe, url_columns):
    """Preprocess and attach core domains for given URL columns in a DataFrame."""
    for col in url_columns:
        dataframe[f'{col}_domain'] = dataframe[col].apply(get_core_domain)

def compare_domains(row, main_domain_col, comparison_domain_cols):
    """Compares main domain with a list of other domains and assigns numerical identifiers for matches, or -1 if no match."""
    matches = []
    main_domain = row[main_domain_col]
    for index, col in enumerate(comparison_domain_cols):
        comparison_domain = row[col]
        if main_domain and comparison_domain and main_domain == comparison_domain:
            matches.append(index + 1)  # Start at 1 to correspond to URL1, URL2, etc.

    return matches if matches else [-1]  # Return matches or -1 if no matches

# Create 'Abbreviation' from the first letter of each word in 'OfficialName'
# only if 'Abbreviation' column is empty
def create_abbreviation(name):
    if pd.isna(name):
        return ""
    return ''.join(word[0] for word in name.split())

def get_domain_without_tld(url):
    if pd.isna(url):
        return ""  # Return an empty string or None, as preferred
    extracted = tldextract.extract(url)
    return extracted.domain  # Return only the domain part without the suffix

# Function to check if any word from 'OfficialName' is in the URL
def check_words_in_url(words, url):
    if pd.isna(words) or pd.isna(url):
        return False
    words = words.split()
    return any(word in url for word in words)

# Function to check if 'Abbreviation' is in the URL
def check_abbreviation_in_url(abbreviation, url):
    if pd.isna(abbreviation) or pd.isna(url):
        return False
    return abbreviation in url

def extract_tlds(url):
    """ Extracts the TLD from a URL."""
    if pd.isna(url):
        return None
    match = re.search(r'\.\w+($|\s|\/)', url)
    if match:
        return match.group(0).strip().strip('/')
    return None

