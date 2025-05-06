Let me create an improved "Download the Results" section using the provided code sample.

# Metagrapho HTR Image Processor

A Python toolkit for handwritten text recognition (HTR) processing using the [Metagrapho API](https://www.metagrapho.com/).

## Overview

This toolkit provides convenient scripts to submit handwritten text for automated recognition and processing. You can:

- Submit local image files (with corresponding XML layouts)
- Submit images directly via URL
- Choose from various HTR and line detection models
- Store and manage job metadata
- Download processed results (optional)

## Prerequisites

- Python 3.8 or higher
- Required packages:
  - `requests`
  - `metagrapho_api` (included in repository)
  - `xml2json` (included in repository)

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install requests
```

3. Ensure `metagrapho_api.py` and `xml2json.py` are in your project directory

## Usage

### Option 1: Submit via URL

```bash
python start_job_for_image_via_url.py \
  --username USER \
  --password your_password \
  --image_path images/0001_p001.jpg \
  --htr_model Bullinger \
  --job_name output_metadata
```

### Option 2: Submit via Base64 (Local File)

```bash
python start_job_for_image_via_base64.py \
  --username USER \
  --password your_password \
  --image_path images/0001_p001.jpg \
  --htr_model Bullinger \
  --job_name output_metadata
```

### Download the Results

Use the `download_results_from_json.py` script to retrieve processed results from completed jobs:

```bash
python download_results_from_json.py \
  --username USER \
  --password your_password \
  --json_file job_metadata.json \
  --tar_dir results \
  --save_image
```

Parameters:
- `--username`: Your Metagrapho API username
- `--password`: Your Metagrapho API password
- `--json_file`: Path to the JSON file containing job information
- `--tar_dir`: Directory where results will be saved (default: "results")
- `--save_image`: (Optional) Flag to download and save the processed image

The script will:
1. Load job information from the specified JSON file
2. Check the status of each job
3. Download processed results for completed jobs
4. Optionally download the original images

## Output

Job metadata is saved as JSON files with the following structure:

```json
{
  "16310985": {
    "status": "WAITING",
    "process_id": 16310985,
    "image_url": "...",
    "htr_model": 309593,
    "line_detection_model": 51962
  }
}
```

## Available Models

### HTR Models

| Model Name | ID | Notes |
|------------|-------|------|
| Text Titan | 309593 | General purpose |
| Bullinger | private | May require special access |
| German Giant | 50870 | Optimized for German text |

### Line Detection Models

| Model Name | ID |
|------------|-------|
| Default | 51962 |

## Advanced Usage

- The scripts provide basic job submission and status checking
- For continuous polling or waiting for job completion, consider extending the scripts
- Results can be downloaded once processing is complete

## License

This project is released under the MIT License.

## Support

