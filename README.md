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

3. DataSetCreatot.ipnyb

4. DataPreperation