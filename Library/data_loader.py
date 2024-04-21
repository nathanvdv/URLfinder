import pandas as pd
import os

def load_data(parquet_directory):
    dataframes = {}
    if os.path.exists(parquet_directory):
        parquet_files = [f for f in os.listdir(parquet_directory) if f.endswith('.parquet')]
        for parquet_file in parquet_files:
            filepath = os.path.join(parquet_directory, parquet_file)
            df = pd.read_parquet(filepath)
            key = os.path.splitext(parquet_file)[0]
            dataframes[key] = df
        return dataframes
    else:
        raise FileNotFoundError(f"Directory does not exist: {parquet_directory}")
