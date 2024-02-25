"""Manage database."""

from typing import List, Tuple, Union
from pprint import pprint, pformat

from app.core.utility.logger_setup import get_logger
from app.core.utility.utils import read_json_file, overwrite_json_file

log = get_logger()


class Database:
    """Manage database.
    
    NOTE:
        Database is a local JSON file
    """

    def __init__(self, filepath: str = "database.json") -> None:
        """TODO."""
        self.db_filepath = filepath

        self.db = read_json_file(self.db_filepath)
        log.debug(f"Database file loaded: {pformat(self.db)}")
        if self.db is None:
            log.fatal(f"Failed to read database file: {self.db_filepath}")

    def remove_all_businesses(self) -> bool:
        """TODO."""
        log.info("Removing all businesses ...")
        overwrite_json_file(self.db_filepath, {})
        return True

    def get_all_business_info(self) -> dict:
        """TODO."""
        log.info("Getting all business info ...")
        self.db = read_json_file(self.db_filepath)
        return self.db

    def create_business(self, name: str, description: str, specifics: str) -> bool:
        """TODO."""
        log.info(f"Creating business: {name}")
        self.db = read_json_file(self.db_filepath)
        
        # Increment next business ID number available
        next_id = len(self.db) + 1
        business_info = {
            "name": name,
            "description": description,
            "specifics": specifics,
        }
        self.db[str(next_id)] = business_info
        overwrite_json_file(self.db_filepath, self.db)
        return True, business_info

    def get_all_business_ids(self) -> List[int]:
        """TODO."""
        log.info(f"Getting all business IDs ...")
        self.db = read_json_file(self.db_filepath)
        return [int(id) for id in self.db.keys()]

    def get_business_info(self, id: int = None, name: str = None) -> Union[dict, None]:
        """TODO."""
        log.info(f"Getting business info: {id} ...")
        self.db = read_json_file(self.db_filepath)
        if id:
            return self.db.get(str(id), {})
        if name:
            for _, business_info in self.db.items():
                if business_info.get("name") == name:
                    return business_info
        log.error(f"Failed to get business info. No ID or name provided.")
        return None
        

    def set_business_info(self, id: str, key: str, value: str) -> bool:
        """TODO."""
        log.info(f"Setting business info: {id} ...")
        self.db = read_json_file(self.db_filepath)
        business_info = self.db.get(id, {})
        business_info[key] = value
        self.db[id] = business_info
        overwrite_json_file(self.db_filepath, self.db)
        return True
