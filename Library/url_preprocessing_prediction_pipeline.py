import re
import pandas as pd
from data_preprocessing_ML import (
    clean_extract_domain, load_data, 
    preprocess_domains, compare_domains, create_abbreviation, get_domain_without_tld, 
    check_words_in_url, check_abbreviation_in_url, extract_tlds
)
from difflib import SequenceMatcher
import Levenshtein
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer

# Extract top-level domain (TLD) for each URL
def extract_tld(url):
        if pd.isna(url):
            return ""
        parts = url.split('.')
        return parts[-1] if len(parts) > 1 else ""
    
def is_subsequence(official, url):
        it = iter(url)
        return all(c in it for c in official)

def jaccard_similarity(set1, set2):
    """ Calculate Jaccard similarity score. """
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)

def check_subsequence(company, url):
    """ Check if all characters in the company name can be found in sequence in the URL. """
    it = iter(url)
    return all(char in it for char in company)

def sequence_match_score(a, b):
    """ Use SequenceMatcher to find how similar two strings are. """
    return SequenceMatcher(None, a, b).ratio()

def levenshtein_distance_score(a, b):
    """ Calculate the Levenshtein distance between two strings. """
    return Levenshtein.distance(a, b)

def safe_set_conversion(text):
    """ Convert a text string to a set of characters, handling None safely. """
    if not text:
        return set()
    return set(text)

def cosine_similarity_score(a, b):
    """ Calculate the cosine similarity between two strings. """
    if not a or not b:
        return 0.0

    if len(a) < 3 or len(b) < 3:
        return 0.0  # Strings are too short for meaningful comparison

    vectorizer = CountVectorizer(analyzer='char', ngram_range=(2, 3))
    vectors = vectorizer.fit_transform([a, b])

    if vectors.shape[1] == 0:
        return 0.0  # No features extracted, possibly due to containing only stop words

    similarity = cosine_similarity(vectors)
    return similarity[0, 1]


def hamming_distance_score(a, b):
    """ Calculate the Hamming distance between two strings. """
    return sum(ch1 != ch2 for ch1, ch2 in zip(a, b))

def ngram_overlap_score(a, b):
    """ Calculate the n-gram overlap between two strings. """
    n = 3  # Adjust n-gram size as needed
    a_ngrams = set([a[i:i+n] for i in range(len(a)-n+1)])
    b_ngrams = set([b[i:i+n] for i in range(len(b)-n+1)])

    # Check for zero denominator
    if len(a_ngrams) == 0 or len(b_ngrams) == 0:
        return 0.0

    overlap = len(a_ngrams.intersection(b_ngrams))
    return overlap / min(len(a_ngrams), len(b_ngrams))
    
def process_url_data(dataset_query_path, search_results_paths):
    # Load data
    merged_dataset = load_data(dataset_query_path, search_results_paths)
    # Lowercase all URL columns before processing
    #merged_dataset = merged_dataset.head(100) --> only for testing
    print(f'shape of the dataset: {merged_dataset.shape}')
    url_columns = ['URL'] + [f'URL{i}' for i in range(1, 6)]
    for col in url_columns:
        merged_dataset[col] = merged_dataset[col].str.lower()
    # Initialize 'OfficialName_cleaned' and perform cleaning operations
    merged_dataset['OfficialName_cleaned'] = merged_dataset['OfficialName'].str.lower()
    merged_dataset['OfficialName'] = merged_dataset['OfficialName'].str.lower() # Lowercase the 'OfficialName' column
    merged_dataset['OfficialName_cleaned'] = merged_dataset['OfficialName_cleaned'].str.replace(r"\[.*?\]", "", regex=True) # Remove text within brackets (including the brackets)
    merged_dataset['OfficialName_cleaned'] = merged_dataset['OfficialName_cleaned'].str.replace(r"\(.*?\)", "", regex=True)
    merged_dataset['OfficialName_cleaned'] = merged_dataset['OfficialName_cleaned'].str.replace('-', '', regex=True) # Remove hyphens from 'OfficialName'
    merged_dataset['Abbreviation'] = merged_dataset.apply(
        lambda row: create_abbreviation(row['OfficialName_cleaned']) if pd.isna(row['Abbreviation']) else row['Abbreviation'],
        axis=1
        ) # Abbreviation creation if none is given
    
    # Define the URL columns you are working with, e.g., 'URL', 'URL1', 'URL2', etc.
    url_columns = ['URL'] + [f'URL{i}' for i in range(1, 6)]
    url_columns_without_official =[f'URL{i}' for i in range(1, 6)]
    # Preprocess the domains to extract the core domain
    preprocess_domains(merged_dataset, url_columns)
    # Extract and append domain features for each URL column with a suffix indicating the column
    for col in url_columns:
        # Extract clean domain first
        merged_dataset[f'{col}_clean_domain'] = merged_dataset[col].apply(clean_extract_domain)
    # Compare domains and add the comparison results to the DataFrame
    comparison_domain_cols = [f'{col}_clean_domain' for col in url_columns if col != 'URL']
    merged_dataset['domain_matches'] = merged_dataset.apply(
        lambda row: compare_domains(row, 'URL_clean_domain', comparison_domain_cols), axis=1
    )
    print('domains are cleaned')
    # Calculate the length of each 'URL(i)_domain'
    for col in url_columns_without_official:
        domain_col = f'{col}_domain'
        if domain_col in merged_dataset.columns:
            # Apply the extraction of domain without TLD
            merged_dataset[f'{col}_core_domain'] = merged_dataset[domain_col].apply(get_domain_without_tld)
            # Calculate the length of the domain without TLD
            merged_dataset[f'{col}_domain_length'] = merged_dataset[f'{col}_core_domain'].str.len()
    merged_dataset['Abbreviation'] = merged_dataset['Abbreviation'].str.lower() # Lowercase the 'OfficialName' column
    
    for col in url_columns:
        if f'{col}_clean_domain' in merged_dataset.columns:
            # Check if any word from 'OfficialName' is in the URL
            merged_dataset[f'{col}_has_official_word'] = merged_dataset.apply(
                lambda row: check_words_in_url(row['OfficialName_cleaned'], row[col]), axis=1).astype(int)
            # Check if 'Abbreviation' is in the URL
            merged_dataset[f'{col}_has_abbreviation'] = merged_dataset.apply(
                lambda row: check_abbreviation_in_url(row['Abbreviation'], row[col]), axis=1).astype(int)
    merged_dataset['OfficialName_cleaned'] = merged_dataset['OfficialName_cleaned'].str.replace(' ', '', regex=True) # Remove spaces
    # Calculate the length of 'OfficialName_cleaned'
    merged_dataset['OfficialName_cleaned_length'] = merged_dataset['OfficialName_cleaned'].str.len()
    # Calculate the length of 'Abbreviation'
    
    merged_dataset['Abbreviation_length'] = merged_dataset['Abbreviation'].str.len()
    
    # Find all tlds
    all_tlds = set()
    # Columns to check
    url_columns = [f'URL{i}_clean_domain' for i in range(1, 6)]
    # Loop through each column, apply the function, and update the set of TLDs
    for col in url_columns:
        # Apply the extract_tlds function to the column
        current_tlds = merged_dataset[col].apply(extract_tlds)
        # Drop None values and update all_tlds set
        all_tlds.update(tld for tld in current_tlds if tld is not None)
    
    merged_dataset = merged_dataset.fillna('NaN')
    
    # List of TLDs to exclude
    tlds = all_tlds
    # Compile regex pattern outside the function for efficiency
    tld_pattern = r'\.(' + '|'.join([re.escape(tld.strip('.')) for tld in tlds]) + ')$'
    url_columns = [f'URL{i}_clean_domain' for i in range(1, 6)]
    def extract_until_tld(url):
        """Removes the last TLD from the URL if it matches the predefined list."""
        if pd.isna(url):
            return ""  # Handle NaN values
        # Replace the last occurrence of TLD
        url = re.sub(tld_pattern, "", url)
        return url
    for col in url_columns:
        merged_dataset[f'{col}_before_tld'] = merged_dataset[col].apply(extract_until_tld)
    print('Domains are cleaned and NaN has been filled')
    
    url_columns_without_tld = [f'URL{i}_clean_domain_before_tld' for i in range(1, 6)]
    # Parallel application of functions
    print('These calculations will loop 4 times:')
    for col in url_columns_without_tld:
        merged_dataset[f'{col}_official_jaccard'] = merged_dataset.apply(
            lambda row: jaccard_similarity(safe_set_conversion(row['OfficialName']), safe_set_conversion(row[col])), axis=1)
        print('official jaccard done')
        merged_dataset[f'{col}_abbrev_jaccard'] = merged_dataset.apply(
            lambda row: jaccard_similarity(safe_set_conversion(row['Abbreviation']), safe_set_conversion(row[col])), axis=1)
        print('abbrev jaccard done')
        merged_dataset[f'{col}_official_is_subsequence'] = merged_dataset.apply(
            lambda row: check_subsequence(row['OfficialName'], row[col]), axis=1).astype(int)
        print('official is subsequence done')
        merged_dataset[f'{col}_abbrev_is_subsequence'] = merged_dataset.apply(
            lambda row: check_subsequence(row['Abbreviation'], row[col]), axis=1).astype(int)
        print('abbrev is subsequence done')
        merged_dataset[f'{col}_official_seq_match'] = merged_dataset.apply(
            lambda row: sequence_match_score(row['OfficialName'], row[col]), axis=1)
        print('official seq match done')
        merged_dataset[f'{col}_abbrev_seq_match'] = merged_dataset.apply(
            lambda row: sequence_match_score(row['Abbreviation'], row[col]), axis=1)
        print('abbrev seq match done')
        # Applying Levenshtein distance calculations
        merged_dataset[f'{col}_official_levenshtein'] = merged_dataset.apply(
            lambda row: levenshtein_distance_score(row['OfficialName'], row[col]), axis=1)
        print('official levenshtein done')
        merged_dataset[f'{col}_abbrev_levenshtein'] = merged_dataset.apply(
            lambda row: levenshtein_distance_score(row['Abbreviation'], row[col]), axis=1)
        print('abbrev levenshtein done')
        merged_dataset[f'{col}_official_cosine_similarity'] = merged_dataset.apply(
            lambda row: cosine_similarity_score(row['OfficialName'], row[col]), axis=1)
        print('official cosine similarity done')
        merged_dataset[f'{col}_abbrev_cosine_similarity'] = merged_dataset.apply(
            lambda row: cosine_similarity_score(row['Abbreviation'], row[col]), axis=1)
        print('abbrev cosine similarity done')
        merged_dataset[f'{col}_hamming_distance'] = merged_dataset.apply(
            lambda row: hamming_distance_score(row['OfficialName'], row[col]), axis=1)
        print('hamming distance done')
        merged_dataset[f'{col}_ngram_overlap'] = merged_dataset.apply(
            lambda row: ngram_overlap_score(row['OfficialName'], row[col]), axis=1)
        print('ngram overlap done')
    print('Loop is finished')
    return merged_dataset

def prepare_features_and_targets(merged_dataset):
    # Prepare feature matrix X
    feature_columns = [
        'URL1_has_official_word', 'URL1_has_abbreviation',
        'URL2_has_official_word', 'URL2_has_abbreviation',
        'URL3_has_official_word', 'URL3_has_abbreviation',
        'URL4_has_official_word', 'URL4_has_abbreviation',
        'URL5_has_official_word', 'URL5_has_abbreviation',
        'OfficialName_cleaned_length', 'Abbreviation_length'
    ] + [
        f'{col}_{metric}' for col in [f'URL{i}_clean_domain_before_tld' for i in range(1, 6)]
        for metric in [
            'official_jaccard', 'abbrev_jaccard',
            'official_is_subsequence', 'abbrev_is_subsequence',
            'official_seq_match', 'abbrev_seq_match',
            'official_levenshtein', 'abbrev_levenshtein',
            'official_cosine_similarity', 'abbrev_cosine_similarity',
            'hamming_distance', 'ngram_overlap'
        ]
    ]
    X = merged_dataset[feature_columns]

    # Encode multilabel target
    mlb = MultiLabelBinarizer()
    y_encoded = mlb.fit_transform(merged_dataset['domain_matches'])
    return X, y_encoded

