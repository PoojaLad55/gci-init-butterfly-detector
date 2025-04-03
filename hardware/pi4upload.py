import os
import sys
import json
from dotenv import load_dotenv
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.auth import ServiceAccountCredentials

load_dotenv() #load the .env

"""file_path = "./config/service-acc-file.json"

with open (file_path, "r") as f:
    print(f)"""

json_creds = os.getenv("GOOGLE_SERVICE_ACCOUNT")
if not json_creds:
    sys.exit("Error: Service account credentials not found in environment variables")

scopes = ['https://www.googleapis.com/auth/drive.file']
try: 
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_creds, scopes)
except Exception as e:
    sys.exit(f"Error: Unable to tload credentials. {e}")


#GoogleAuth object to set the credentials
gauth = GoogleAuth()
gauth.credentials = credentials
drive = GoogleDrive(gauth)

#Automatic uploading the images sent as a list for now
#upload_file_list = ['testimage1.jpg', 'testimage2.jpg'] 

#Uploading image from command line
if (len(sys.argv) !=2):
    raise ValueError("Improper listing of arguments. One and only one arg is required in the following format: python uploadtest.py <image_file>")


capture = sys.argv[1]

if not os.path.isfile(capture):
    sys.exit(f"Error: File '{capture}' not found.")

try: 
    gfile = drive.CreateFile({'parents':[{'id': '105LoQfxNjeQbvgJ49IFkgy5IFDTinJ8p'}]})
    gfile.SetContentFile(capture)
    gfile.Upload()
    print(f"Uploaded {capture} successfully")
except Exception as e:
    sys.exit(f"Error: Upload failed. {e}")

