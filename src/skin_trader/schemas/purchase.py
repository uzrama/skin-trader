from pydantic import BaseModel, Field, computed_field


class PurchaseRequest(BaseModel):
    market: str = Field(..., description="Name of market")
    name: str = Field(..., description="Name of item")
    price: float = Field(..., ge=0.0, description="Price from the parser")
    popularity: int = Field(default=0, ge=0, description="Popularity indicator")

    @computed_field
    @property
    def purchase_limit(self) -> int:
        """Calculate the limit of purchases based on item popularity or price.

        Returns:
            int: Number of purchases (1 for popularity < 250, 5 for < 5000, else 2).
        """

        if self.price >= 3:
            if self.popularity <= 700:
                return 1
            else:
                return 2

        if self.popularity < 250:
            return 1
        elif self.popularity <= 700:
            return 2
        elif self.popularity <= 2000:
            return 3
        elif self.popularity <= 4000:
            return 4
        else:
            return 7
