import math
import re

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#Define the main class
class Sheets():
    #Define the main variables
    def __init__(self) -> None:
        self.service = None
        self.values = None
        self.SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        self.SPREADSHEET_ID = None
        self.RANGE_NAME = "engenharia_de_software!B4:H28"
    #Define the methods to initialize the googlespreadsheet API
    def build(self):
        #Code avaialable in the googlespreadsheet API documentation in https://developers.google.com/sheets/api/quickstart/python?hl=pt-br
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json",self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        try:
            #With the authentication process is done, then the service is initialized
            self.service = build("sheets", "v4", credentials=creds)
        except Exception as e:
            print(e)
            print("Error")
            return False
        
    #Function that get the data from the spreadsheet
    def get(self, id, rng):
        try:
            sheet = self.service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=id, range=rng)
                .execute()
            )
            #Set the values from the spreadsheet and set the spreadsheet id and the name of the spreadsheet
            self.values = result.get("values", [])
            self.SPREADSHEET_ID = id
            self.RANGE_NAME = re.sub(r"!.*", "", rng)
            
        except Exception as e:
            print(e)
            print("Error")
            return False
    
    #Function that update the state of the student, receiving the range and the value to be put in each student
    def updateState(self,range, value):
        try:
            result = (
                 self.service.spreadsheets()
                .values()
                .update(spreadsheetId=self.SPREADSHEET_ID, range=f"{self.RANGE_NAME}!G{range}", valueInputOption="RAW", body=value)
                .execute()
            )
        except Exception as e:
            print(e)
            print("Error")
            return False
    
    #Function that update the minimum value to be approved in the final exam, for any other stundent the default value is 0
    def naf(self, range, value={"values": [[0]]}):
        try:
            result = (
                 self.service.spreadsheets()
                .values()
                .update(spreadsheetId=self.SPREADSHEET_ID, range=f"{self.RANGE_NAME}!H{range}", valueInputOption="RAW", body=value)
                .execute()
            )
        except Exception as e:
            print(e)
            print("Error")
            return False
    
    #Helper function to get the index of the row
    def helperIndex(self,row):
        return self.values.index(row) + 4
    
    #Function that iterate over the values of the spreadsheet, it calculates the avarage and the percentage of the classes attended
    #Then it updates the state of the student with a if and else condition
    def iterate(self):
        for row in self.values:
            #Define the values to be checked
            #For a personal choice I preferred to divide by 30 to get the scale of the avarege to 0-10
            avg = (int(row[2]) + int(row[3]) + int(row[4])) / 30
            percentAttendClasses = (60 - int(row[1])) / 60 * 100
            range = self.helperIndex(row)
            print(f"Name: {row[0]}, Avarage: {round(avg,2)}, Frequency: {round(percentAttendClasses,2)}%")
            if percentAttendClasses < 75:
                print(f"The stundent {row[0]} was disapproved by absence")
                #The updateState function is called and passed the range and the value to be updated
                self.updateState(range,{"values": [['Reprovado por falta']]})
                self.naf(range)
            elif (avg < 5):
                print(f"The student {row[0]} was reproved by avarage")
                self.updateState(range,{"values": [['Reprovado por média']]})
                self.naf(range)
            elif (avg >= 5 and avg < 7):
                #In this situation besides the "Situação" column be updated the "Nota para aprovação final" column is updated as well
                # With the formula bellow
                print(f"The student {row[0]} is in the final exam")
                self.updateState(range,{"values": [['Exame final']]})
                #The formula calculates how much the students needs to pass the final exam
                self.naf(range,{"values": [[math.ceil(avg*10 - (2 * 5))]]})
            else:
                #If the student get any avarage above 7 he is approved	
                print(f"The student {row[0]} was approved")  
                self.updateState(range,{"values": [['Aprovado']]})
                self.naf(range)
    #Method that executes the whole process
    def run(self, spreadsheetId, range):
        print("Iniciando...")
        self.build()
        self.get(spreadsheetId, range)
        self.iterate()
        print("Fim")


#Instantiate the class and call the run method
if __name__ == "__main__":
    sheet = Sheets()
    sheet.run("1Ycy3hBFdTtfpyjA1q8bi-GmNx9f7kktRvldmqfYUqqQ","engenharia_de_software!B4:H28")
