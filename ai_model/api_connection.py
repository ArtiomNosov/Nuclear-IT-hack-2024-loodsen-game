import requests
import base64
import uuid

sber_id = "08b96aae-68dc-4180-9cfe-86e7e3a36bd0"

sber_secret = "2df7ab68-b4ba-42a8-91e8-f8cf86057f49"

auth_key = "MDhiOTZhYWUtNjhkYy00MTgwLTljZmUtODZlN2UzYTM2YmQwOjJkZjdhYjY4LWI0YmEtNDJhOC05MWU4LWY4Y2Y4NjA1N2Y0OQ=="


url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

def token(auth,scope ='GIGACHAT_API_PERS'):
  
  rq_uid = str(uuid.uuid4())

  payload={
  'scope': scope
    }
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': rq_uid,
    'Authorization': f"Basic {auth}"
  }
  response = requests.request("POST", url, headers=headers, data=payload,verify=False)
  return response


