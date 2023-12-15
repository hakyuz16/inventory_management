import datetime
from typing import List, Optional

from pandas import DataFrame
from pydantic import root_validator
from pydantic.main import BaseModel


class WarehouseOrder(BaseModel):
    shop_order_id: str
    warehouse_id: str
    pack_line: str
    products: List[str]
    warehouse_costs: float
    shipment_costs: float
    order_datetime: datetime.datetime
    total_costs: Optional[float]
    quantity: Optional[int]

    @property
    def key(self):
        return self.warehouse_id, self.pack_line

    @root_validator
    def set_quantity(cls, values):
        values['quantity'] = len(values.get('products'))
        return values

    @root_validator
    def set_total_costs(cls, values):
        values['total_costs'] = values.get('warehouse_costs') + values.get('shipment_costs')
        return values


class LostSalesShopOrder(BaseModel):
    shop_order_id: str
    order_datetime: datetime.datetime
    unsourceable_products: List[str]


class SourcingOption(BaseModel):
    warehouse_orders: List[WarehouseOrder]
    lost_sales_shop_orders: LostSalesShopOrder
    penalty: float = 0

    @property
    def costs(self):
        return sum([warehouse_order.total_costs for warehouse_order in \
                    self.warehouse_orders]) + self.penalty


class PackLine(BaseModel):
    name: str
    type: str
    capacity: int
    cost_per_product: float


class Warehouse(BaseModel):
    name: str
    pack_lines: Optional[List[PackLine]]
    cost_per_shipment: float
    stock_capacity: int
    products_on_stock: Optional[set] = None

    def update_stock(self, stock_allocation: DataFrame):
        products = set(
            stock_allocation[stock_allocation[self.name]]['product_id'])
        if len(products) > self.stock_capacity:
            raise ValueError(f"stock allocation on warehouse {self.name} exceeds "
                             f"capacity (stock size: {len(products)}, capacity "
                             f"constraint: {self.stock_capacity}), please "
                             f"allocate stock within capacity")
        self.products_on_stock = products
        return self

    def get_pack_lines(self, type):
        return [pl for pl in self.pack_lines if pl.type == type]


class SimulationResult(BaseModel):
    warehouse_orders: Optional[DataFrame]
    lost_sales: Optional[DataFrame]
    total_costs: Optional[float]

    def __init__(self, warehouse_orders):
        super().__init__()
        # this could also be done with default_factory
        self.warehouse_orders = DataFrame([
            warehouse_order.dict()
            for warehouse_orders_per_so in warehouse_orders
            for warehouse_order in warehouse_orders_per_so.warehouse_orders
        ])

        self.total_costs = round(sum([warehouse_order.costs
                                for warehouse_order in warehouse_orders]),2)

        lost_sales = DataFrame([
            warehouse_order.lost_sales_shop_orders.dict()
            for warehouse_order in warehouse_orders
        ]).rename({'unsourceable_products':'product_id'},axis=1)
        self.lost_sales = lost_sales.explode('product_id').dropna().reset_index(drop=True)

    class Config:
        arbitrary_types_allowed = True

    def show_aggregated_results(self):
        print(f"Warehouse orders sourced: {self.warehouse_orders.shop_order_id.count()}")
        print(f"Total costs: {self.total_costs}")
        print(f"Lost sales: {self.lost_sales.product_id.count()} products")
