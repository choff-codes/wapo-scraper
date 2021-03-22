# Washington Post Election Tracker

The Washington Post had a webpage where they updated the number of votes in each key state for both the candidates, primarily focused on PA, AZ, and NV. This tool 
used Python's webscraping to pull that data, compare it against the last values, and toss that data into a Google Sheet to build a more accurate trend of the results.

By the 10th update for each state, I had an accurate estimate of the final ballot count each state would finish at for each candidate (days before they finished
counting), with an buffer of ~5k votes.

![alt-text](https://github.com/choff97/wapo-scraper/blob/main/Screenshots/AZ_Spreadsheet_Pic.png?raw=true)
