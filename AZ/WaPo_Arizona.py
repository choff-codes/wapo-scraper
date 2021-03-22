import re
from urllib.request import urlopen
import os, ssl
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime

f = open("spreadsheet_ID.txt", "r")
ID_TO_USE = f.readline()
f.close()

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = ID_TO_USE
RANGE_NAME = 'AZ!A:C'

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

url = "https://www.washingtonpost.com/elections/election-results/arizona-2020/"

# TO:DO
# - Align Nevada with the rest of the states
# - Upload to Github with screenshots of the spreadsheet in the readme

# Pull the webpage and use a regular expression to grab the vote values
page = urlopen(url)
html = page.read().decode("utf-8")

pattern = "<div class=.font-xxxxs font-xxs-ns gray-dark.>([0-9]+(,[0-9]+)+)<\/div>"
match_results = re.findall(pattern, html, re.IGNORECASE)

biden_votes = match_results[0]
trump_votes = match_results[1]

creds = None

# Grab the previous values from the stored file
f = open("results_AZ.txt", "r")
biden_file_string = f.readline()
trump_file_string = f.readline()
f.close()

# Clean the strings to compare with the new integers
biden_file_int = (biden_file_string[0:9]).replace(',', '')
trump_file_int = (trump_file_string[0:9]).replace(',', '')
correct_scraped_biden = (biden_votes[0]).replace(',', '')
correct_scraped_trump = (trump_votes[0]).replace(',', '')

biden_diff = int(correct_scraped_biden) - int(biden_file_int)
trump_diff = int(correct_scraped_trump) - int(trump_file_int)

now = datetime.now()
current_time = now.strftime("%H:%M:%S")

# Print to terminal if no change to either has occured, otherwise - update
if biden_diff == 0 and trump_diff == 0:
    print("The difference in both was 0!\n")
    print("Last checked: " + current_time)
else:
    # The file token.pickle stores the access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, it'll ask for a log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Grabs the appropriate row used to update the Google Sheet
    f = open("rowNum.txt", "r")
    rowNumString = f.readline()
    f.close()

    rowNum = int(rowNumString)
    updateNum = rowNum - 1

    # These are the update variables built to inject into the spreadsheet
    timeValues = [
        [
            current_time
        ]
    ]

    timeBody = {
        'values': timeValues
    }

    updateValues = [
        [
            updateNum,
            biden_diff,
            trump_diff
        ]
    ]

    body = {
        'values': updateValues
    }

    int_scraped_biden = int(correct_scraped_biden)
    int_scraped_trump = int(correct_scraped_trump)

    totalValues = [
        [
            int_scraped_biden,
            int_scraped_trump
        ]
    ]

    totalBody = {
        'values': totalValues
    }

    newRowNum = rowNum + 1

    # Increment the row number for the next potential call
    f = open("rowNum.txt", "w")
    f.write(str(newRowNum))
    f.close()

    # Build the proper range, then update all three necessary portions of the
    # spreadsheet with the new information
    rangeVal = 'AZ!A' + str(rowNum) + ':C' + str(rowNum)

    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=rangeVal,
        valueInputOption='RAW', body=body).execute()

    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range='AZ!L20',
        valueInputOption='RAW', body=totalBody).execute()

    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range='AZ!F2',
        valueInputOption='RAW', body=timeBody).execute()

    # Keep tabs of the trend data in a back-up file
    f = open("trend_AZ.txt", "a")
    f.write("\n\n" + str(biden_diff) + "\n" + str(trump_diff))
    f.close()

    print("The difference in Biden votes is" + "\n")
    print(biden_diff)

    print("The difference in Trump votes is" + "\n")
    print(trump_diff)
    print("Results pulled at: " + current_time)

    # Update the results file for future comparisons
    f = open("results_AZ.txt", "w")
    f.write(biden_votes[0] + "\n" + trump_votes[0])
    f.close()
