# URLfinder
This document contains explanations and instructions about the URL Finder Tool. For each application, it is explained what it does and how to use it.

1. ZipDownloader.ipynb
The ZipDownloader file is the first file needed to start. After installing the necessary packages (downloading dependencies), a dataset from the KBO is downloaded via the "Automatic Zip Downloader". 

In this file, web scraping is done via selenium, first, a Chrome driver is installed and set up in setup_driver(). The second function, wait_for_download_completion(), ensures that the driver waits for the download of the requested zip folder. The timer is currently set to 1000 seconds, meaning the driver will give an error message if the download is not completed after 1000 seconds. Of course, this timeout can be adjusted.
In the login(driver) function, the driver navigates to the KBO website and fills in the user's login credentials. For privacy purposes, these credentials have been replaced with #'s here. The user of the tool can create an account on the site themselves and fill in their details here.

In the navigate_and_download() function, the driver navigates to the right link on the website. Once the driver arrives on the intended site, it searches for the KboOpenData_Full.zip. By adding latest_date = max(file_dates.keys()) and latest_file_url = file_dates[latest_date], we make sure that the most recent zip folder is downloaded.

2. ZipFileReader.ipynb
In the second application, the zip folder is unpacked and read. The first function ensures that we always use the latest downloaded zip folder. 
The second function, namely extract_and_convert_to_parquet(), ensures that the zip folder is first unpacked (extractall) and then read (df = pd.read_csv(csv_file_path)). In the next step, problematic columns (here 'Zipcode') are converted to correct types (here string). Then, these dataframes are converted to parquet files (to_parquet) to use less memory.
In the main processing logic, we specify how the directories are named and ensure that the function ends with a completed update ("Update completed.") or with the message that there is no new zip file that needs to be processed.

3. DataSetCreator.ipnyb
In DataSetCreator, the parquet files are read and converted into dataframes. Then, these dataframes are linked and filtered. 

In the first part "Load Parquet Files into DataFrames," the directory is first set to ExtractedFiles, after which all parquet files are placed in a dictionary. To check how these dataframes currently appear, each dataframe is iterated over to show information (df.info) and print the first few rows (df.head).

In the second step, named "Filtered Dataframe," the dataframes are filtered based on the specific needs of the user. We start with the "denomination" dataframe. Here, the choice is made to filter only the companies that specify at least a Dutch-language name (Language == 2). We then split the "TypeOfDenomination" into "Officialname," "Abbreviation", and "TradeName". These designations correspond to when TypeOfDenomination takes on the values 1, 2, or 3. Next, we do the same in the "address" dataframe for Dutch zip codes, municipalities, street names, and house numbers. Finally, the emails, phone numbers, and URLs in the "contact" dataframe are renamed.
In the final lines of code, the filtered dataframes are combined. This combined dataframe is then merged using the primary key "EntityNumber," as this is the only column present in each dataframe, and is unique for every company. Finally, "EntityNumber" is set as the index and displayed to the user so they can verify whether the dataframes have been correctly combined.

In "Filtering" we filter out the rows where no CountryNL is found. In "Filtering on URL" we create a parquet file only containing rows that contain a URL. We safe this dataframe with URLs to potentially use as a training set for our Machine Learning model later on. To be sure we have one entry per company, we lastly delete all duplicates by keeping the first row of each EntityNumber. 

In df_final.info we take a look at the attributes of our final URL dataframe. We also print out the first 50 instances to take a closer see what the dataframe looks like. 

In "Analyse and visualize the final URL dataframe" we take a closer look into the statistics of our URL dataframe. First we print out some numerical statistics such as 'count' and 'unique'. Next, we  examine numerically the top 5 municipalities where the companies (with a filled URL) are located, after which we create a bar plot of the top 10 municipalities and a heatmap to visualize the missing data. Note that these numbers are solely for the dataframe made out of instances with a URL.
Based on the heatmap, we decide to drop the columns that occur infrequently. 

In the section "Visualizing duplicate entries in rows," we identify duplicate URLs. The existence of 741 duplicate entries may not necessarily indicate an issue. It's possible that different subsidiaries are referring to the same website.

Lastly we save the combined dataset as a parquet file and as a csv. 
4. DataPreperation.ipynb