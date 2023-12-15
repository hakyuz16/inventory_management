from typing import List, Tuple
from pydantic import BaseModel

from .models import SourcingOption


class ProductionCapacityEntry(BaseModel):
    warehouse: str
    pack_line: str
    type: str
    capacity: int
    available_capacity: int = None
    key: Tuple = None

    def __init__(self, **data):
        super().__init__(**data)
        # Init the available capacity
        self.available_capacity = self.capacity
        # Create a custom key for identification, consisting of all relevant fields
        self.key = (self.warehouse, self.pack_line)

    def reset_capacity(self):
        self.available_capacity = self.capacity

    def is_available(self, order_size):
        return self.available_capacity >= order_size


class CapacityTracker(dict):
    def __init__(self, warehouses: List):
        super().__init__(
            {(wh.name, pl.name): ProductionCapacityEntry(**{"warehouse": wh.name,
                                                            "pack_line": pl.name, "type": pl.type,
                                                            "capacity": pl.capacity})
             for wh in warehouses for pl in wh.pack_lines}
        )

    def update_capacity(self, sourcing_option: SourcingOption):
        for warehouse_order in sourcing_option.warehouse_orders:
            self[warehouse_order.key].available_capacity -= warehouse_order.quantity

    def reset_capacities(self):
        for pack_line in self:
            self[pack_line].reset_capacity()

    def get_available_pack_lines(self) -> List[Tuple]:
        return [self[pack_line].key for pack_line in self if self[pack_line].is_available]

    def get_capacity(self, pack_line_key: Tuple):
        return self[pack_line_key].available_capacity
