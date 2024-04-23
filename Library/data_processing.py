import zipfile
import pandas as pd
import os

from regex import F

def extract_and_convert_to_parquet(zip_filename, extraction_directory):
    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extractall(extraction_directory)

    for root, dirs, files in os.walk(extraction_directory):
        for file in files:
            if file.endswith('.csv'):
                csv_file_path = os.path.join(root, file)
                parquet_file_path = os.path.join('ExtractedFiles', file.replace('.csv', '.parquet'))
                df = pd.read_csv(csv_file_path, low_memory= False)
                if 'Zipcode' in df.columns:
                    df['Zipcode'] = df['Zipcode'].astype(str)
                df.to_parquet(parquet_file_path)
