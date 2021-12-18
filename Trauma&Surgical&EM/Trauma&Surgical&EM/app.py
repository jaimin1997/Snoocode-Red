from __future__ import print_function
from flask.wrappers import Request
import xlrd
import json
from flask import Flask, render_template, request


import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
gauth = GoogleAuth()           
drive = GoogleDrive(gauth)  

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/')
def main_route():
	return render_template('TraumaForm.html')

@app.route('/submit_form', methods=['POST'])
def submit_form():
    wb = xlrd.open_workbook("Trauma.xlsx")
    sheet = wb.sheet_by_index(0)
    question_list = []
    level_list = []
    for each in range(sheet.nrows):
        question = sheet.cell_value(each, 0)
        level = sheet.cell_value(each, 1)
        question_list.append(question)
        level_list.append(level)
    levelOneCount = 0
    levelTwoCount = 0
    levelThreeCount = 0
    levelFourCount = 0
    for req in request.form:
        if req not in ['add', 'facility', 'dis', 'region']:
            if request.form.get(req) != 'No':
                index = question_list.index(request.form.get(req))
                level = ''
                if level_list[index]:
                    level = level_list[index].split(",")
                    for each in level:
                        if each.strip() == "Level 1":
                            levelOneCount += 1
                        elif each.strip() == 'Level 2':
                            levelTwoCount += 1
                        elif each.strip() == 'Level 3':
                            levelThreeCount += 1
                        elif each.strip() == 'Level 4':
                            levelFourCount += 1
               
    levelList = [levelOneCount, levelTwoCount, levelThreeCount, levelFourCount]
    maximum = max(levelList)
    levelString = ''
    if maximum != 0:
        indices = []
        for i in range(len(levelList)):
            if levelList[i] == maximum:
                indices.append(i)
        triggeredLevel = indices[::-1][0]
        levelString = ''
        if triggeredLevel == 0:
            levelString = 'Level 1'
        if triggeredLevel == 1:
            levelString = 'Level 2'
        if triggeredLevel == 2:
            levelString = 'Level 3'
        if triggeredLevel == 3:
            levelString = 'Level 4'
    html = '<p>Health Facility : ' + request.form.get('facility') + '</p><p>Snoocode Address : ' + request.form.get('add') + '</p><p>District/Municipality/Metropolis : ' + request.form.get('dis') + '</p><p>Region : '  + request.form.get('region') + '</p><p>Triggered Level : ' + levelString + '</p>'
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        file1 = drive.CreateFile({'parents': [{'id': '1s3lup_uVaKcM4KpNdZEpHq3I_rovsYzy'}],'title': 'Crimson-Project-Data.xlxs'})  
        file1.SetContentString('Health Facility : ' + request.form.get('facility') + '\n\nSnoocode Address : ' + request.form.get('add') + '\n\nDistrict/Municipality/Metropolis : ' + request.form.get('dis') + '\n\nRegion : '  + request.form.get('region') + '\n\nTriggered Level : ' + levelString + '')
        file1.Upload({'convert': True})

    return html


# main driver function
if __name__ == '__main__':

	# run() method of Flask class runs the application
	# on the local development server.
	app.run()
