
import argparse
import base64
from datetime import datetime
import json
import os
from pathlib import Path

from metagrapho_api import MetagraphoAPI
from xml2json import convert_xml2json


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
    parser.add_argument('--image_path', type=str, default='images/0001_p001.jpg', help='URL of the image')
    parser.add_argument('--htr_model', type=str, default="Bullinger", help='HTR model ID')
    parser.add_argument('--job_name', type=str, default="default", help='Name to save the job')
    args = parser.parse_args()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    args.job_name = f"{args.job_name}_{timestamp}"

    return args

def process_image(api, args):
    """Process the image using the Metagrapho API. args should include an image URL."""
    # Submit by URL
    
    IMAGE_PATH = args.image_path
    XML_PATH = Path(IMAGE_PATH).parent / Path("xml") / (Path(IMAGE_PATH).stem + ".xml")
    HTR_ID = HTR_MODEL_IDs[args.htr_model]

    with open(IMAGE_PATH, "rb") as image_file:
        base64_str = base64.b64encode(image_file.read()).decode("utf-8")

    with open(XML_PATH, "r", encoding="utf-8") as f:
        xml_input = f.read()

    layout_json = convert_xml2json(xml_input)

    process_id = api.submit_image_by_base64(base64_str, HTR_MODEL_IDs[args.htr_model], layout_content=layout_json)

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
                "image_path": str(IMAGE_PATH),
                "htr_model": HTR_ID,
                "layout_xml": str(XML_PATH)
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
