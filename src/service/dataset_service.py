import os
import pandas as pd
import requests
import zipfile
from io import BytesIO
import logging
from tqdm import tqdm
import pydicom

logger = logging.getLogger(__name__)

os.makedirs("data", exist_ok=True)

class DatasetService:
    TEXT_DATA_URL = "https://data.mendeley.com/public-files/datasets/s6bgczr8s2/files/ed86d033-5078-4658-948f-94c13e8b2291/file_downloaded"
    IMAGE_DATA_URL = "https://data.mendeley.com/public-files/datasets/k57fr854j2/files/eab74360-db27-4ec5-ade3-7b1b8d88e2db/file_downloaded"

    @staticmethod
    def download_text_data():
        response = requests.get(DatasetService.TEXT_DATA_URL, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            chunk_size = 8192
            file_path = "data/text_data.xlsx"

            with open(file_path, "wb") as f, tqdm(
                total=total_size, unit='B', unit_scale=True, desc="Downloading Excel"
            ) as pbar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

            logger.info("Downloaded Excel file successfully: %s", file_path)

            df = pd.read_excel(file_path)
            file_csv = "data/text_data.csv"
            df.to_csv(file_csv, index=False)
            logger.info("Converted to CSV successfully: %s", file_csv)
        else:
            logger.error("Failed to download text data, status code: %d", response.status_code)

    @staticmethod
    def download_image_data():
        response = requests.get(DatasetService.IMAGE_DATA_URL, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            chunk_size = 8192

            zip_path = "data/image_data.zip"
            with open(zip_path, "wb") as f, tqdm(
                total=total_size, unit='B', unit_scale=True, desc="Downloading ZIP"
            ) as pbar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

            extract_path = "data/image_data"
            os.makedirs(extract_path, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(extract_path)
            logger.info("Downloaded and extracted images to %s", extract_path)

            os.remove(zip_path)
        else:
            logger.error("Failed to download image data, status code: %d", response.status_code)

    @staticmethod
    def get_image_metadata(idx):
        metadata_path = f"data/image_data/01_MRI_DATA/{idx}"

        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Path not found: {metadata_path}")

        metadata_list = []

        for root, _, files in os.walk(metadata_path):
            for file in files:
                if file.lower().endswith('.ima'):
                    file_path = os.path.join(root, file)
                    try:
                        dcm = pydicom.dcmread(file_path, stop_before_pixels=True)

                        # Convert DICOM Dataset to a flat dictionary
                        metadata = {
                            "File": file_path,
                        }
                        for elem in dcm:
                            keyword = elem.keyword or elem.name or str(elem.tag)
                            metadata[keyword] = str(elem.value)

                        metadata_list.append(metadata)

                    except Exception as e:
                        logger.warning(f"Cannot read {file_path}: {e}")
        
        return metadata_list
        