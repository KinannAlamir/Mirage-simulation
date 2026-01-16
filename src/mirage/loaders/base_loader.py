"""Base loader class for spreadsheet data."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Any

import pandas as pd


class BaseLoader(ABC):
    """Base class for data loaders."""

    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path
        self._data: Optional[pd.DataFrame] = None

    def load_excel(
        self,
        file_path: Optional[Path] = None,
        sheet_name: str | int = 0,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Load data from Excel file."""
        path = file_path or self.file_path
        if not path:
            raise ValueError("No file path provided")
        
        self._data = pd.read_excel(path, sheet_name=sheet_name, **kwargs)
        return self._data

    def load_csv(
        self,
        file_path: Optional[Path] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Load data from CSV file."""
        path = file_path or self.file_path
        if not path:
            raise ValueError("No file path provided")
        
        self._data = pd.read_csv(path, **kwargs)
        return self._data

    @abstractmethod
    def parse(self) -> Any:
        """Parse loaded data into domain models."""
        pass

    @property
    def data(self) -> Optional[pd.DataFrame]:
        """Get the loaded data."""
        return self._data
