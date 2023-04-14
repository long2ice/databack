import json
from enum import Enum

from pydantic import BaseModel


class Order(str, Enum):
    asc = "asc"
    desc = "desc"


class Sort(BaseModel):
    field: str
    order: Order


class Query(BaseModel):
    limit: int = 10
    offset: int = 0
    sorts: str | None = None

    @property
    def orders(self):
        orders = []
        if self.sorts:
            for sort in json.loads(self.sorts):
                order = sort.get("order")
                field = sort.get("field")
                if order == Order.asc:
                    orders.append(field)
                else:
                    orders.append(f"-{field}")
        return orders
