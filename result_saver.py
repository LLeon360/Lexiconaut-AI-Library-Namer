import json
import os
import logging
from typing import List
from models import ResultItem

import uuid

logger = logging.getLogger(__name__)

class ResultSaver:
    def __init__(self, filename: str) -> None:
        self.filename: str = filename
    
    def save_results(self, results: List[ResultItem]) -> None:
        def serialize_uuid(obj):
            if isinstance(obj, uuid.UUID):
                return str(obj)
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        with open(self.filename, 'w') as f:
            json.dump([result.model_dump() for result in results], f, indent=2, default=serialize_uuid)
        
    def append_results(self, new_results: List[ResultItem]) -> None:
        existing_results: List[ResultItem] = self.load_results()
        combined_results: List[ResultItem] = existing_results + new_results
        self.save_results(combined_results)

    def load_results(self) -> List[ResultItem]:
        try:
            with open(self.filename, 'r') as f:
                content = f.read().strip()
                if not content:  # Check if file is empty
                    return []
                data = json.loads(content)
                return [ResultItem(**{**item, 'id': uuid.UUID(item['id'])}) for item in data]
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {self.filename}. File might be empty or corrupted.")
            return []

    def toggle_star(self, item_id: uuid.UUID) -> None:
        results = self.load_results()
        for result in results:
            if result.id == item_id:
                result.starred = not result.starred
                break
        self.save_results(results)

    def delete_result(self, item_id: uuid.UUID) -> None:
        results = self.load_results()
        results = [result for result in results if result.id != item_id]
        self.save_results(results)