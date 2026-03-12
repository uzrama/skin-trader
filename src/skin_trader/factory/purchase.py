from skin_trader.schemas.purchase import PurchaseRequest


class PurchaseFactory:
    """
    Factory for creating purchase requests.
    """

    @staticmethod
    def create_purchase(data: dict[str, dict[str, str]]):
        """
        Creates a purchase request from a dictionary.

        Args:
            data: The dictionary containing the purchase data.

        Returns:
            A purchase request.
        """
        market = data["firstMarket"]["market"]
        name = data["itemInfo"]["marketHashName"]
        price = data["firstMarket"]["price"]
        popularity = data["secondMarket"]["popularity"]
        item_dict = {
            "market": market,
            "name": name,
            "price": price,
            "popularity": popularity,
        }
        return PurchaseRequest.model_validate(item_dict)
