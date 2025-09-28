import concurrent
import json
import os
from tqdm import tqdm
from service.dataset_service import DatasetService

class ImaService:
    BASE_PATH = "data/image_data/01_MRI_DATA"
    OUTPUT_FOLDER = "data/metadata"

    @staticmethod
    def parse_all():
        base_path = ImaService.BASE_PATH
        output_folder = ImaService.OUTPUT_FOLDER
        os.makedirs(output_folder, exist_ok=True)
        folder_list = sorted(os.listdir(base_path))

        def process(idx):
            metadata = DatasetService.get_image_metadata(idx)
            filename = f"{int(idx)}.json"
            filepath = os.path.join(output_folder, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

        with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
            futures = [executor.submit(process, folder_name) for folder_name in folder_list if folder_name.isdigit() and len(folder_name) == 4]

            for _ in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Parsing metadata"):
                pass