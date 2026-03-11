import asyncio
import io
import logging
from pathlib import Path
from typing import ClassVar
import aiofiles
import pandas as pd
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class BaseCSVRepository[T]:
    """
    Base class for CSV repositories.

    This class provides a generic interface for interacting with CSV files as a database.
    It uses pandas for data manipulation and aiofiles for asynchronous file operations.

    Attributes:
        model: The Pydantic model to use for data validation.
        file_path: The path to the CSV file.
    """

    model: ClassVar[type[BaseModel]]
    file_path: Path

    def __init__(self, file_path: str):
        """
        Initializes the repository.

        Args:
            file_path: The path to the CSV file.
        """
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def _get_columns(self) -> list[str]:
        """Retrieves a list of columns from a Pydantic model"""
        return list(self.model.model_fields)

    async def _ensure_file_exists(self) -> None:
        """Creates a CSV file with headers if it does not exist"""
        if not self.file_path.exists():
            columns = self._get_columns()
            df = pd.DataFrame(columns=columns)
            await self._save_dataframe(df)

    async def _write_file(self, content: str) -> None:
        """
        Writes content to the CSV file.

        Args:
            content: The content to write.
        """
        async with aiofiles.open(self.file_path, "w", encoding="utf-8") as file:
            await file.write(content)

    async def _read_file(self) -> str:
        """
        Reads content from the CSV file.

        Returns:
            The content of the file.
        """
        await self._ensure_file_exists()
        async with aiofiles.open(self.file_path) as file:
            return await file.read()

    async def _save_dataframe(self, df: pd.DataFrame) -> None:
        """
        Saves a pandas DataFrame to the CSV file.

        Args:
            df: The DataFrame to save.
        """
        csv_content = await asyncio.to_thread(df.to_csv, index=False)
        await self._write_file(csv_content)

    async def _load_dataframe(self) -> pd.DataFrame:
        """
        Loads a pandas DataFrame from the CSV file.

        Returns:
            The loaded DataFrame.
        """
        try:
            content = await self._read_file()
            if not content.strip():
                return pd.DataFrame(columns=self._get_columns())
            csv_buffer: io.StringIO = io.StringIO(content)
            df: pd.DataFrame = await asyncio.to_thread(pd.read_csv, csv_buffer)
            if df.empty:
                return pd.DataFrame(columns=self._get_columns())
            return df
        except Exception as e:
            logger.warning(f"Error loading CSV {self.file_path}: {e}")
            return pd.DataFrame(columns=self._get_columns())
