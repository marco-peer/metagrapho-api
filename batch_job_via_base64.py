
import argparse
import base64
from datetime import datetime
import json
import os
from pathlib import Path
from random import randint

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
    parser.add_argument('--image_directory', type=str, default='images/', help='directory with images')
    parser.add_argument('--htr_model', type=str, default="Bullinger", help='HTR model ID')
    parser.add_argument('--job_name', type=str, default="default", help='Name to save the job')
    args = parser.parse_args()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    args.job_name = f"{args.job_name}_{timestamp}"

    return args

def process_image(api, image_path, htr_model):
    """Process the image using the Metagrapho API. args should include an image URL."""
    # Submit by URL

    HTR_ID = HTR_MODEL_IDs[htr_model]

    with open(image_path, "rb") as image_file:
        base64_str = base64.b64encode(image_file.read()).decode("utf-8")



    XML_PATH = Path(image_path).parent / Path("xml") / (Path(image_path).stem + ".xml")
    if not XML_PATH.exists():
        print(f"XML file not found for {image_path}. Skipping Layout")
        XML_PATH = None
    else:
        with open(XML_PATH, "r", encoding="utf-8") as f:
            xml_input = f.read()

        layout_json = convert_xml2json(xml_input)

    process_id = api.submit_image_by_base64(base64_str, HTR_ID, layout_content=layout_json)
    # process_id = randint(0,10000)

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
                "image_path": str(image_path),
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

    image_extensions = (".jpg", ".jpeg", ".png")
    imgs = [img for img in sorted(list(Path(args.image_directory).glob("**/*"))) if img.suffix.lower() in image_extensions]                  
    job_f = {}
    print(f"Found {len(imgs)} images in {args.image_directory}")
    for img in imgs:
        # Process each image
        json_file = process_image(api, img, args.htr_model)
        job_f.update(json_file)


    # Logout
    api.logout()

    os.makedirs("jobs", exist_ok=True)
    with open(f"jobs/{args.job_name}.json", 'w') as f:
        json.dump(job_f, f, indent=4)
