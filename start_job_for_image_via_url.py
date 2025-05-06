
import argparse
from datetime import datetime
import json
import os

from metagrapho_api import MetagraphoAPI

HTR_MODEL_IDs = {
    "Text Titan" : 309593,
    "Bullinger" : "private",
    "German Giant" : 50870
}

LINE_DETECTION_MODEL_IDs = {
    "default" : 51962
}


def parse_args():
    parser = argparse.ArgumentParser(description="Process HTR image parameters.")
    
    parser.add_argument('--username', type=str, required=True, help='Username for authentication')
    parser.add_argument('--password', type=str, required=True, help='Password for authentication')
    parser.add_argument('--image_url', type=str, default='https://bullinger-stiftung.ch/wp-content/uploads/2022/01/Jost-von-Meggen-an-Bullinger_01.png', help='URL of the image')
    parser.add_argument('--htr_model', type=str, default="Bullinger", help='HTR model ID')
    parser.add_argument('--line_detection_model', type=str, default="default", help='Line detection model ID')
    parser.add_argument('--job_name', type=str, default="default", help='Name to save the job')
    args = parser.parse_args()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    args.job_name = f"{args.job_name}_{timestamp}"

    return args

def process_image(api, args):
    """Process the image using the Metagrapho API. args should include an image URL."""
    # Submit by URL
    
    IMAGE_URL = args.image_url
    HTR_ID = HTR_MODEL_IDs[args.htr_model]
    LINE_DETECTION_MODEL_ID = LINE_DETECTION_MODEL_IDs[args.line_detection_model]

    process_id = api.submit_image_by_url(IMAGE_URL, HTR_ID, LINE_DETECTION_MODEL_ID)

    json_file = {}
    # Wait for processing to complete
    if process_id:
        status = api.check_status(process_id)
    else:
        print("Failed to submit image.")
        process_id = -1
        status = "NOT_SUBMITTED"
 
    json_file[process_id] = {
                "status": status,
                "process_id": process_id,
                "image_url": IMAGE_URL,
                "htr_model": HTR_ID,
                "line_detection_model": LINE_DETECTION_MODEL_ID
            }
    
    return json_file

if __name__ == "__main__":
    args = parse_args()
    
    USERNAME = args.username
    PASSWORD = args.password

    api = MetagraphoAPI(USERNAME, PASSWORD)
    api.authenticate()

    json_file = process_image(api, args)

    # Logout
    api.logout()

    os.makedirs("jobs", exist_ok=True)
    with open(f"jobs/{args.job_name}.json", 'w') as f:
        json.dump(json_file, f, indent=4)
