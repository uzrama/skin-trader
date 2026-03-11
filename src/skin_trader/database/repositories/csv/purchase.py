from typing import final

import pandas as pd

from skin_trader.database.repositories.csv.base import BaseCSVRepository
from skin_trader.schemas.purchase import PurchaseRequest


@final
class PurchaseCSVRepository(BaseCSVRepository[PurchaseRequest]):
    """
    Repository for storing and retrieving purchase requests from a CSV file.
    """

    model = PurchaseRequest

    async def find_all_by_name(self, name: str) -> list[PurchaseRequest] | None:
        """
        Finds all purchase requests by name.

        Args:
            name: The name of the item to find.

        Returns:
            A list of purchase requests, or None if no purchases are found.
        """
        purchases: list[PurchaseRequest] = []
        df = await self._load_dataframe()
        purchase_df = df[df["name"] == name]

        if purchase_df.empty:
            return None

        for _, row in purchase_df.iterrows():
            purchases.append(PurchaseRequest.model_validate(dict(row)))

        return purchases

    async def create(self, purchase: PurchaseRequest) -> PurchaseRequest:
        """
        Creates a new purchase request.

        Args:
            purchase: The purchase request to create.

        Returns:
            The created purchase request.
        """
        df = await self._load_dataframe()

        new_purchase_row = pd.DataFrame([purchase.model_dump()])
        df = pd.concat([df.dropna(axis=1, how="all"), new_purchase_row], ignore_index=True)

        await self._save_dataframe(df)

        return purchase

    async def update(self, purchase: PurchaseRequest):
        """
        Updates a purchase request.

        Args:
            purchase: The purchase request to update.

        Returns:
            The updated purchase request.

        Raises:
            ValueError: If the item is not found or the name already exists.
        """
        df = await self._load_dataframe()

        item_index = df[df["name"] == purchase.name].index
        if item_index.empty:
            raise ValueError(f"Item by name {purchase.name} not found")

        name_check = df[(df["name"] == purchase.name) & (df["name"] != purchase.name)]

        if not name_check.empty:
            raise ValueError(f"Item with name {purchase.name} exist")

        df.loc[item_index[0]] = PurchaseRequest.model_dump(purchase)

        await self._save_dataframe(df)

        return purchase

    async def get_many(self) -> list[PurchaseRequest]:
        """
        Gets all purchase requests.

        Returns:
            A list of all purchase requests.
        """
        purchases: list[PurchaseRequest] = []
        purchase_df = await self._load_dataframe()

        for _, row in purchase_df.iterrows():
            purchases.append(PurchaseRequest.model_validate(dict(row)))

        return purchases
