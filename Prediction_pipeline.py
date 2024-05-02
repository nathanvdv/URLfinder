import os
import pandas as pd
import time
from sklearn.preprocessing import StandardScaler
import joblib
from urllib.parse import urlparse
from duckduckgo_search import DDGS
from sklearn.model_selection import train_test_split
from Library.data_processing import extract_and_convert_to_parquet
from Library.file_management import find_latest_zip_file, get_last_processed_file, update_last_processed_file
from Library.web_driver import setup_driver
from Library.download_utils import wait_for_download_completion
from Library.navigation_utils import login, navigate_and_download
import Library.data_filter_prediction_pipeline as data_filter
import Library.data_loader as data_loader
import Library.data_saver_prediction_pipeline as data_saver_prediction_pipeline
import Library.url_preprocessing_prediction_pipeline as url_preprocessing_prediction_pipeline
import warnings
from pandas.errors import PerformanceWarning

warnings.filterwarnings('ignore', category=PerformanceWarning)




def main_web_interaction():
    driver, download_dir = setup_driver()
    try:
        initial_files = set(os.listdir(download_dir))
        login(driver, "your_username", "your_password")
        if navigate_and_download(driver, download_dir):
            if not wait_for_download_completion(download_dir, initial_files):
                print("Download did not complete within the timeout period.")
    finally:
        driver.quit()

def manage_zip_files():
    zip_directory = 'Zip'
    extracted_files_directory = 'ExtractedFiles'
    if not os.path.exists(extracted_files_directory):
        os.makedirs(extracted_files_directory)
    latest_zip = find_latest_zip_file(zip_directory)
    last_processed = get_last_processed_file(extracted_files_directory)
    if latest_zip and latest_zip != last_processed:
        print(f"Processing new ZIP file: {latest_zip}")
        full_zip_path = os.path.join(zip_directory, latest_zip)
        extract_and_convert_to_parquet(full_zip_path, extracted_files_directory)
        update_last_processed_file(latest_zip, extracted_files_directory)
        print("Update complete.")
    else:
        print("No new ZIP file needs processing.")

def main_data_processing(parquet_directory):
    dataframes = data_loader.load_data(parquet_directory)
    combined_df = data_filter.filter_data(dataframes)
    data_saver_prediction_pipeline.save_data(combined_df)

def scrape_top_urls_ddg(search_query, skip_domains, max_results=10):
    top_urls = []
    ddgs = DDGS()
    try:
        results = ddgs.text(keywords=search_query, max_results=max_results + len(skip_domains))
        for result in results:
            url = result.get('href')
            if url and not any(skip_domain in url for skip_domain in skip_domains):
                top_urls.append(url)
                if len(top_urls) == max_results:
                    break
    except Exception as e:
        print(f"Encountered an error: {e}")
        raise
    return top_urls

def process_and_scrape_data():
    try:
        result_df = pd.read_csv('search_results_DDG.csv')
        collected_data = result_df.to_dict('records')
    except FileNotFoundError:
        collected_data = []

    df = pd.read_parquet("combined_filtered_dataset.parquet")
    print(df.head())
    df['SearchQuery'] = df.apply(lambda row: f"{row['OfficialName']} {row['ZipCode']} {row['Municipality']}", axis=1)
    df.to_csv('dataset_incl_query.csv', index=True)
    total_rows = len(df)
    skip_domains = set(
        ['trendstop.knack.be', 'fincheck.be', 'bizzy.org'
                , 'trendstop.levif.be', 'companyweb.be', 'linkedin.com'
                , 'en.wikipedia.org', 'facebook.com', 'be.linkedin.com'
                , 'instagram.com', 'werkenbijdeoverheid.be', 'dnb.com', 'nl.wikipedia.org'
                , 'youtube.com', 'staatsbladmonitor.be', 'werkenvoor.be'
                , 'twitter.com', 'vlaanderen.be/organisaties', 'jobat.be'
                , 'vdab.be', 'opencorporates.com','www.goldenpages.be',
                'www.immoweb.be', 'be.kompass.com','www.infobel.com',
                'www.bsearch.be', 'www.creditsafe.com','openthebox.be',
                'bedrijvengids.cybo.com','data.be','www.yelp.com',
                'www.goudengids.be','gb.kompass.com','www.cylex-belgie.be',
                'local.infobel.be','www.cybo.com','www.viamichelin.com','lokaal.infobel.be',
                'www.northdata.com','www.tripadvisor.com','www.zoominfo.com',
                'fr.kompass.com','www.openingsuren.vlaanderen','www.info-clipper.com',
                'www.northdata.de','b2bhint.com','www.realo.be',
                'www.pagesdor.be','www.worldpostalcodes.org','www.openingsurengids.be',
                'open-winkel.be','opencorpdata.com','lemariagedelouise.be',
                'www.signalhire.com','www.faillissementsdossier.be','www.bizique.be',
                'www.booking.com','www.hours.be','www.handelsgids.be',
                'foursquare.com','zaubee.com','be.top10place.com',
                'restaurantguru.com','www.zimmo.be','guide.michelin.com',
                'selfcity.be','belgium.worldplaces.me','www.boekhoudkantoren.be',
                'jaarrekening.be'
    ])

    for index, row in df.iterrows():
        if any(d['EntityNumber'] == row['EntityNumber'] for d in collected_data):
            continue  # Skip already processed
        
        search_query = row['SearchQuery']
        entity_number = row['EntityNumber']
        try:
            filtered_urls = scrape_top_urls_ddg(search_query, skip_domains, max_results=5)
            time.sleep(1)  # Simple rate limit

            collected_data.append({
                "EntityNumber": entity_number, 
                "URL1": filtered_urls[0] if len(filtered_urls) > 0 else "",
                "URL2": filtered_urls[1] if len(filtered_urls) > 1 else "",
                "URL3": filtered_urls[2] if len(filtered_urls) > 2 else "",
                "URL4": filtered_urls[3] if len(filtered_urls) > 3 else "",
                "URL5": filtered_urls[4] if len(filtered_urls) > 4 else ""
            })
        except Exception as e:
            print(f"Error encountered: {e}. Waiting before retrying...")
            time.sleep(20)
            continue

        result_df = pd.DataFrame(collected_data)
        result_df.to_csv('search_results_DDG.csv', index=False)
        processed_entries = index + 1 # type: ignore
        percentage_completed = (processed_entries / total_rows) * 100
        print(f"Processed EntityNumber {entity_number}")

    print("All data has been processed and saved.")
    
def load_and_predict():
    X, y_encoded, processed_data = prepare_data()

    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = joblib.load('gradient_boosting_classifier.pkl')
    predictions = model.predict(X_test_scaled)
    
    return predictions, processed_data  # Return processed_data instead of X_test


def prepare_data():
    dataset_query_path = 'dataset_incl_query.csv'
    search_results_paths = ['search_results_DDG.csv']
    # Process data
    processed_data = url_preprocessing_prediction_pipeline.process_url_data(dataset_query_path, search_results_paths)
    # Prepare features and targets
    X, y_encoded = url_preprocessing_prediction_pipeline.prepare_features_and_targets(processed_data)
    return X, y_encoded, processed_data  # Include processed_data in the return


def create_predicted_url_df(processed_data, predictions):
    data = []
    
    for idx, (prediction, entry) in enumerate(zip(predictions, processed_data.itertuples(index=False))):
        predicted_urls = []
        
        if prediction[0] == 1:
            predicted_urls.append('No scraped URL has been found correct')
        if prediction[1] == 1:
            predicted_urls.append(entry.URL1)
        if prediction[2] == 1:
            predicted_urls.append(entry.URL2)
        if prediction[3] == 1:
            predicted_urls.append(entry.URL3)
        if prediction[4] == 1:
            predicted_urls.append(entry.URL4)
        if prediction[5] == 1:
            predicted_urls.append(entry.URL5)

        if not predicted_urls:
            predicted_urls.append('No valid prediction')

        data.append({'Entity Number': entry.EntityNumber, 'Predicted URL': '; '.join(predicted_urls)})

    results_df = pd.DataFrame(data)
    return results_df

def extract_domain_from_urls(df):
    def get_domain(url):
        try:
            # Parse the URL, extract the domain with TLD
            parsed_url = urlparse(url)
            # Getting the domain from the 'netloc' which handles cases with or without 'www.'
            if parsed_url.netloc:
                return parsed_url.netloc
            else:
                # Sometimes, the URL might be passed without HTTP/HTTPS, handle these cases
                # Attempt to handle cases where urlparse does not automatically fill netloc
                return urlparse('http://' + url).netloc
        except Exception as e:
            print(f"Error parsing URL {url}: {str(e)}")
            return ""  # Return empty string if there's an error

    # Apply the get_domain function to each URL in the 'Predicted URL' column
    df['Predicted URL Domain'] = df['Predicted URL'].apply(
        lambda x: '; '.join([get_domain(url.strip()) for url in x.split(';') if url.strip()])
    )
    return df

def save_to_parquet(df, file_path):
    try:
        df.to_parquet(file_path, index=False, compression='snappy')
        print(f"Data successfully saved to {file_path}")
    except Exception as e:
        print(f"An error occurred while saving to Parquet: {str(e)}")

def main():
    # Step 1: Setup web driver and manage downloads
    print("Starting web interactions and downloads...")
    main_web_interaction()

    # Step 2: Manage and process ZIP files
    print("Processing ZIP files...")
    manage_zip_files()

    # Step 3: Load, filter, analyze, and save data
    print("Loading and processing data...")
    parquet_directory = 'ExtractedFiles'
    main_data_processing(parquet_directory)

    # Step 4: Scrape additional data from the web
    print("Scraping additional data...")
    process_and_scrape_data()

    # Step 5: Perform machine learning preprocessing + prediction
    print("Preprocessing data for machine learning and starting the prediction process..")

    # Load data and make predictions
    predictions, processed_data = load_and_predict()  # Updated to receive processed_data

    # Create the predicted URL DataFrame using processed_data
    predicted_df = create_predicted_url_df(processed_data, predictions)
    
    # Extract domains from the predicted URLs
    predicted_df = extract_domain_from_urls(predicted_df)
    print(predicted_df.head(10))
    print("Model predictions completed.")
    
    # Step 6: Save the predictions to a Parquet file
    
    # Save the DataFrame to a Parquet file
    save_to_parquet(predicted_df, 'predicted_urls.parquet')

if __name__ == "__main__":
    print("Script execution started.")
    main()
    print("Script execution finished.")