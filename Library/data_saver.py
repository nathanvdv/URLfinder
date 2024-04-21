import pandas as pd

def save_data(df_final_URL, parquet_file_path='./combined_filtered_dataset.parquet', csv_file_path='./df_final_URL.csv'):
    # Save the combined DataFrame as a Parquet file
    df_final_URL.to_parquet(parquet_file_path)
    print(f"Combined and filtered DataFrame saved as Parquet file at: {parquet_file_path}")

    # Save the combined DataFrame as a CSV file
    df_final_URL.to_csv(csv_file_path, index=False)
    print(f"Combined and filtered DataFrame saved as CSV file at: {csv_file_path}")
