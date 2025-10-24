import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from pymongo import MongoClient, UpdateOne
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class UnifiedDataManager:
    def __init__(self):
        self.client = MongoClient(settings.mongodb_url)
        self.db = self.client[settings.mongodb_database]
        logger.info(f"Connected to MongoDB: {settings.mongodb_database}")

    def cleanup_collections(self):
        """Remove existing collections before fresh ingestion"""
        existing_collections = self.db.list_collection_names()
        for collection in existing_collections:
            if collection.endswith(('_videos', '_categories')):
                self.db.drop_collection(collection)
                logger.info(f"Dropped collection: {collection}")

    def process_videos_csv(self, region: str, file_path: Path) -> None:
        try:
            df = pd.read_csv(
                file_path,
                encoding='utf-8',
                encoding_errors='replace',
                on_bad_lines='skip'
            )

            videos = []
            for _, row in df.iterrows():
                video = row.to_dict()
                video['region'] = region
                video['ingestion_date'] = datetime.now()
                video['last_updated'] = datetime.now()
                
                # Clean numeric fields
                numeric_fields = ['view_count', 'likes', 'dislikes', 'comment_count']
                for field in numeric_fields:
                    try:
                        video[field] = int(float(video.get(field, 0)))
                    except (ValueError, TypeError):
                        video[field] = 0
                
                videos.append(video)

            collection = self.db[f"{region.lower()}_videos"]
            operations = [
                UpdateOne(
                    {'video_id': video['video_id']},
                    {'$set': video},
                    upsert=True
                ) for video in videos
            ]

            result = collection.bulk_write(operations)
            logger.info(f"{region} videos: {result.upserted_count} inserted, {result.modified_count} updated")

        except Exception as e:
            logger.error(f"Error processing {region} videos: {str(e)}")
            raise

    def process_categories_json(self, region: str, file_path: Path) -> None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            categories = data.get('items', [])
            for category in categories:
                category['region'] = region
                category['ingestion_date'] = datetime.now()
                category['last_updated'] = datetime.now()

            collection = self.db[f"{region.lower()}_categories"]
            operations = [
                UpdateOne(
                    {'id': category['id']},
                    {'$set': category},
                    upsert=True
                ) for category in categories
            ]

            result = collection.bulk_write(operations)
            logger.info(f"{region} categories: {result.upserted_count} inserted, {result.modified_count} updated")

        except Exception as e:
            logger.error(f"Error processing {region} categories: {str(e)}")
            raise

    def cleanup(self):
        self.client.close()
        logger.info("MongoDB connection closed")

def main():
    try:
        manager = UnifiedDataManager()
        
        # Cleanup existing collections
        manager.cleanup_collections()
        
        dataset_path = Path(__file__).parent.parent.parent.parent / "dataset"
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset directory not found at {dataset_path}")

        regions = ['US', 'GB', 'DE', 'CA', 'FR', 'IN', 'JP', 'KR', 'MX', 'RU']
        
        for region in regions:
            # Process CSV files
            video_file = dataset_path / f"{region}videos.csv"
            if video_file.exists():
                logger.info(f"Processing {region} videos...")
                manager.process_videos_csv(region, video_file)

            # Process JSON files
            category_file = dataset_path / f"{region}_category_id.json"
            if category_file.exists():
                logger.info(f"Processing {region} categories...")
                manager.process_categories_json(region, category_file)

        logger.info("Unified data ingestion completed successfully")

    except Exception as e:
        logger.error(f"Error in unified data ingestion: {str(e)}")
        raise
    finally:
        if 'manager' in locals():
            manager.cleanup()

if __name__ == "__main__":
    main()