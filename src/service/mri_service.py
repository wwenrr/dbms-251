import csv
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from service.redis_service import RedisService
import logging

logger = logging.getLogger(__name__)

class MriService:
    CSV_PATH = 'data/text_data.csv'
    METADATA_PATH = 'data/metadata'

    @staticmethod
    def process_mri_data(max_workers=32):
        RedisService.configure()
        RedisService.create_index()

        if not os.path.exists(MriService.CSV_PATH):
            logger.error(f"CSV file not found: {MriService.CSV_PATH}")
            return

        if not os.path.exists(MriService.METADATA_PATH):
            logger.error(f"Metadata folder not found: {MriService.METADATA_PATH}")
            return

        with open(MriService.CSV_PATH, newline='', encoding='utf-8') as csvfile:
            reader = list(csv.DictReader(csvfile))

        def process_row(row):
            patient_id = row.get("Patient ID")
            notes = row.get("Clinician's Notes", "")

            if not patient_id:
                return

            metadata_file = os.path.join(MriService.METADATA_PATH, f"{int(patient_id)}.json")
            if not os.path.exists(metadata_file):
                metadata = []
            else:
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                except json.JSONDecodeError:
                    metadata = []

            # Lưu thông tin patient (notes) riêng
            patient_key = f"patient:{patient_id}"
            RedisService.json_set(patient_key, {
                "notes": notes
            })

            # Lưu từng object metadata riêng biệt với patient_id để dễ query
            for idx, item in enumerate(metadata):
                meta_key = f"metadata:{patient_id}:{idx}"
                # Thêm patient_id vào mỗi metadata object để tạo TAG index dễ dàng
                item['patient_id'] = patient_id
                RedisService.json_set(meta_key, item)

            return f"Saved patient {patient_id}"

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_row, row) for row in reader]

            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing patients"):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error processing a row: {e}")
