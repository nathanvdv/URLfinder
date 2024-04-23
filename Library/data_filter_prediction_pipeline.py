import pandas as pd
from functools import reduce

def filter_data(dataframes):
    # Filter for OfficialName
    official_name_df = dataframes['denomination'][
        (dataframes['denomination']['TypeOfDenomination'] == 1) & 
        (dataframes['denomination']['Language'] == 2)
    ][['Denomination', 'EntityNumber']].copy()
    official_name_df.rename(columns={'Denomination': 'OfficialName'}, inplace=True)

    # Filter for Abbreviation
    abbreviation_df = dataframes['denomination'][
        (dataframes['denomination']['TypeOfDenomination'] == 2) & 
        (dataframes['denomination']['Language'] == 2)
    ][['Denomination', 'EntityNumber']].copy()  
    abbreviation_df.rename(columns={'Denomination': 'Abbreviation'}, inplace=True)

    # Filter for ZipCode
    zipcode_df = dataframes['address'][
        (dataframes['address']['TypeOfAddress'] == "REGO")
    ][['Zipcode', 'EntityNumber']].copy()  
    zipcode_df.rename(columns={'Zipcode': 'ZipCode'}, inplace=True)

    # Filter for Municipality
    Municipality_df = dataframes['address'][
        (dataframes['address']['TypeOfAddress'] == "REGO")
    ][['MunicipalityNL', 'EntityNumber']].copy()  
    Municipality_df.rename(columns={'MunicipalityNL': 'Municipality'}, inplace=True)

    # Filter for Street
    Street_df = dataframes['address'][
        (dataframes['address']['TypeOfAddress'] == "REGO")
    ][['StreetNL', 'EntityNumber']].copy()  
    Street_df.rename(columns={'StreetNL': 'Street'}, inplace=True)

    # Filter for HouseNumber
    HouseNumber_df = dataframes['address'][
        (dataframes['address']['TypeOfAddress'] == "REGO")
    ][['HouseNumber', 'EntityNumber']].copy()  
    HouseNumber_df.rename(columns={'HouseNumber': 'HouseNumber'}, inplace=True)

    # Filter for URL
    URL_df = dataframes['contact'][
        (dataframes['contact']['EntityContact'].isin(['ENT', 'EST'])) & 
        (dataframes['contact']['ContactType'] == 'WEB') &
        (dataframes['contact']['Value'].notna())
    ][['Value', 'EntityNumber']].copy()
    URL_df.rename(columns={'Value': 'URL'}, inplace=True)

    # Filter for NaceCode
    Activity_df = dataframes['activity'][
         (dataframes['activity']['Classification'] == 'MAIN')
    ][['NaceCode', 'EntityNumber']].copy()
    Activity_df.rename(columns={'NaceCode': 'NaceCode'}, inplace=True)

    # Merge all filtered DataFrames
    df_list = [official_name_df, abbreviation_df, zipcode_df, Municipality_df, Street_df, HouseNumber_df, URL_df, Activity_df]
    combined_df = reduce(lambda left, right: pd.merge(left, right, on='EntityNumber', how='left'), df_list)

    # Drop duplicates based on EntityNumber
    combined_df.drop_duplicates(subset='EntityNumber', keep='first', inplace=True)

    # Select desired columns
    combined_df = combined_df[['EntityNumber', 'OfficialName', 'Abbreviation', 'ZipCode', 'Municipality', 'Street', 'HouseNumber', 'URL', 'NaceCode']]

    return combined_df