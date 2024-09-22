import json
import os
import logging
from typing import List
from models import ResultItem

logger = logging.getLogger(__name__)

class ResultSaver:
    def __init__(self, filename: str) -> None:
        self.filename: str = filename

    def load_results(self) -> List[ResultItem]:
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                logger.debug(f"Data loaded from file: {data}")
                return [ResultItem(**item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        
    def append_results(self, new_results: List[ResultItem]) -> None:
        existing_results: List[ResultItem] = self.load_results()
        combined_results: List[ResultItem] = existing_results + new_results
        self.save_results(combined_results)
    
    def save_results(self, results: List[ResultItem]) -> None:
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        
        with open(self.filename, 'w') as f:
            json.dump([result.model_dump(by_alias=True) for result in results], f, indent=2)

    def toggle_star(self, index: int) -> None:
        results = self.load_results()
        if 0 <= index < len(results):
            results[index].starred = not results[index].starred
            self.save_results(results)

    def delete_result(self, index: int) -> None:
        results = self.load_results()
        if 0 <= index < len(results):
            del results[index]
            self.save_results(results)