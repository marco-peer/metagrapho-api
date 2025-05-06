


import argparse
import json
import os
from pathlib import Path

import requests

from metagrapho_api import MetagraphoAPI


def parse_args():
    parser = argparse.ArgumentParser(description="Process HTR image parameters.")
    
    parser.add_argument('--username', type=str, required=True, help='Username for authentication')
    parser.add_argument('--password', type=str, required=True, help='Password for authentication')
    parser.add_argument('--json_file', type=str, default="default", help='JSON file that includes the job information')
    parser.add_argument('--tar_dir', type=str, default="results", help='Password for authentication')

    parser.add_argument('--save_image', action='store_true', help='Whether to save the processed image')
    args = parser.parse_args()

    return args


def download_image_from_url(image_url, output_folder='images'):
    """Download an image from a URL and save it locally."""
    os.makedirs(output_folder, exist_ok=True)
    image_path = os.path.join(output_folder, Path(image_url).name)

    response = requests.get(image_url)
    if response.status_code == 200:
        with open(image_path, 'wb') as f:
            f.write(response.content)
        print(f"Image saved to {image_path}")
    else:
        raise Exception(f"Failed to download image. Status code: {response.status_code}")


if __name__ == "__main__":
    args = parse_args()
    
    USERNAME = args.username
    PASSWORD = args.password

    api = MetagraphoAPI(USERNAME, PASSWORD)
    api.authenticate()
    
    # load the json file
    with open(args.json_file, 'r') as f:
        json_file = json.load(f)

    for job_id, job_info in json_file.items():
        print(f"Processing job ID: {job_id}")
        status = api.check_status(job_id)


        # Download the image if the flag is set and there is an image URL
        if args.save_image:
            image_url = job_info.get("image_url", None)
            if image_url:
                print(f"Downloading image from {image_url}")
                download_image_from_url(image_url, output_folder=os.path.join(args.tar_dir, 'images'))


        # Download the result
        if status == "FINISHED":
            api.download_result(job_id, image_name=job_id, output_folder=args.tar_dir)

    # Logout
    api.logout()