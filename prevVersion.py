import os.path
import math
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1Ycy3hBFdTtfpyjA1q8bi-GmNx9f7kktRvldmqfYUqqQ"
SAMPLE_RANGE_NAME = "engenharia_de_software!B4:H28"



def main():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)
  
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
        .execute()
    )
    values = result.get("values", [])

    if not values:
      print("No data found.")
      return

    for row in values:
      # Print columns A and E, which correspond to indices 0 and 4.
      media = (int(row[2]) + int(row[3]) + int(row[4])) / 30
      percentAttendClasses = (60 - int(row[1])) / 60 * 100
      print(values.index(row)+4)
      print(f"Nome: {row[0]}, Média: {media}, Frequência: {percentAttendClasses}%")
      if percentAttendClasses < 75:
        print(f"O aluno {row[0]} foi reprovado por falta")
        result = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range=f"engenharia_de_software!G{values.index(row)+4}",
            valueInputOption="RAW",
            body={"values": [['Reprovado por falta']]},
        )
        .execute(),
        
    )
      elif (media < 5):
        print(f"O aluno {row[0]} foi reprovado por média")
        result = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range=f"engenharia_de_software!G{values.index(row)+4}",
            valueInputOption="RAW",
            body={"values": [['Reprovado por média']]},
        )
        .execute(),
        
        )
      elif (media >= 5 and media < 7):
        print(f"O aluno {row[0]} está em exame final")
        result = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range=f"engenharia_de_software!G{values.index(row)+4}",
            valueInputOption="RAW",
            body={"values": [['Exame final']]},
        )
        .execute(),
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range=f"engenharia_de_software!H{values.index(row)+4}",
            valueInputOption="RAW",
            body={"values": [[math.ceil((2 * 5) - media*10)]]},
        )
        .execute(),
        )
      else:
        print(f"O aluno {row[0]} foi aprovado")  
        result = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range=f"engenharia_de_software!G{values.index(row)+4}",
            valueInputOption="RAW",
            body={"values": [['Aprovado por média']]},
        )
        .execute()
        )

  except HttpError as err:
    print(err)


if __name__ == "__main__":
  main()