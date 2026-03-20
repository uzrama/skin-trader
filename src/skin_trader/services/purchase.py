from typing import final
from skin_trader.database.repositories.csv.purchase import PurchaseCSVRepository
from skin_trader.schemas.purchase import PurchaseRequest


@final
class PurchaseCSVService:
    def __init__(self, file_path: str) -> None:
        self.purchase_repository = PurchaseCSVRepository(file_path)

    async def create(self, purchase: PurchaseRequest):
        return await self.purchase_repository.create(purchase)

    async def get_all_by_name(self, name: str) -> list[PurchaseRequest] | None:
        return await self.purchase_repository.find_all_by_name(name)

    async def get_all(self) -> list[PurchaseRequest]:
        return await self.purchase_repository.get_many()
