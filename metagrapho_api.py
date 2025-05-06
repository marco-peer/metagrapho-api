import requests
import time
import os

from pathlib import Path

class MetagraphoAPI:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client_id = 'processing-api-client'
        self.auth_url = 'https://account.readcoop.eu/auth/realms/readcoop/protocol/openid-connect'
        self.api_url = 'https://transkribus.eu/processing/v1'
        self.access_token = None
        self.refresh_token = None

    def authenticate(self):
        url = f"{self.auth_url}/token"
        payload = {
            'grant_type': 'password',
            'username': self.username,
            'password': self.password,
            'client_id': self.client_id
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            print("Authentication successful!")
        else:
            print(f"Authentication failed: {response.status_code} - {response.text}")

    def refresh_access_token(self):
        if not self.refresh_token:
            raise ValueError("No refresh token available. Authenticate first.")

        url = f"{self.auth_url}/token"
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            print("Token refreshed successfully!")
        else:
            print(f"Token refresh failed: {response.status_code} - {response.text}")

    def logout(self):
        if not self.refresh_token:
            raise ValueError("No refresh token available. Authenticate first.")

        url = f"{self.auth_url}/logout"
        payload = {
            'refresh_token': self.refresh_token,
            'client_id': self.client_id
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 204:
            print("Logout successful!")
            self.access_token = None
            self.refresh_token = None
        else:
            print(f"Logout failed: {response.status_code} - {response.text}")

    def submit_image_by_url(self, image_url, htr_id, line_detection_model_id):
        url = f"{self.api_url}/processes"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            "config": {
                "textRecognition": {
                    "htrId": htr_id
                },
                "lineDetection": {
                    "modelId": line_detection_model_id
                }
            },
            "image": {
                "imageUrl": image_url
            }
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"Image submitted successfully! Process ID: {data['processId']}")
            return data['processId']
        else:
            print(f"Image submission failed: {response.status_code} - {response.text}")
            return None

    def check_status(self, process_id):
        url = f"{self.api_url}/processes/{process_id}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            print(f"Process {process_id} status: {status}")
            return status
        else:
            print(f"Failed to check status: {response.status_code} - {response.text}")
            return None

    def download_result(self, process_id, image_name, output_folder='results'):
        url = f"{self.api_url}/processes/{process_id}/page"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/xml'  # Tell server you expect XML
        }

        os.makedirs(output_folder, exist_ok=True)

        response = requests.get(url, headers=headers, stream=True)

        if response.status_code == 200:
            output_path = os.path.join(output_folder, f"{image_name}.xml")
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"✅ Result saved to {output_path}")
            return output_path

        elif response.status_code == 401:
            print("❌ Unauthorized. Check your Bearer token.")
        elif response.status_code == 404:
            print("❌ Process not found or result not ready yet.")
        else:
            print(f"❌ Failed to download result: {response.status_code} - {response.text}")

        return None

    def submit_image_by_base64(self, base64_string, htr_id, layout_content=None):
        url = f"{self.api_url}/processes"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        payload = {
            "config": {
                "textRecognition": {
                    "htrId": htr_id
                }
            },
            "image": {
                "base64": base64_string
            }
        }


        # Optionally include layout information if provided
        if layout_content:
            payload["content"] = layout_content
        else:
            payload["config"]["lineDetection"] = {
                "modelId": 51962 # Default line detection model ID
            }
            
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"Image submitted successfully via base64! Process ID: {data['processId']}")
            return data['processId']
        else:
            print(f"Base64 image submission failed: {response.status_code} - {response.text}")
            return None
        