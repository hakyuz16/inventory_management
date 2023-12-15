import datetime
from itertools import permutations
from typing import Dict, List

from pandas import DataFrame

from .capacity_tracker import CapacityTracker
from .models import WarehouseOrder, LostSalesShopOrder, SourcingOption, Warehouse


class OrderSourcer:

    def __init__(self, stock_allocation: DataFrame, warehouses: Dict, lost_sales_penalty: float):
        self.lost_sales_penalty = lost_sales_penalty
        self.warehouses = [
            (Warehouse.parse_obj(warehouse).update_stock(stock_allocation)
             ) for warehouse in warehouses]
        self.capacity_tracker = CapacityTracker(self.warehouses)

    @staticmethod
    def create_warehouse_orders(order: DataFrame, first_set_of_products: set,
                                second_set_of_products: set):
        first_wh_order = order[order["product_id"].isin(first_set_of_products)].to_dict(
            orient="records")
        second_wh_order = order[(order["product_id"].isin(second_set_of_products)) &
                                (~order["product_id"].isin(
                                    first_set_of_products))].to_dict(orient="records")
        return first_wh_order, second_wh_order

    def create_sourcing_options(self, products: set, warehouse: Warehouse, order_id:
    str, order_datetime: datetime.datetime):
        products_on_stock = warehouse.products_on_stock.intersection(products)
        left_over_products = products.difference(products_on_stock)

        # first try to make a multi
        if len(products_on_stock) > 1:
            multi_pack_lines = warehouse.get_pack_lines('multi')
            for pack_line in multi_pack_lines:
                if self.capacity_tracker[(warehouse.name,
                                          pack_line.name)].is_available(len(products_on_stock)):
                    return (left_over_products, [
                        WarehouseOrder(
                            shop_order_id=order_id,
                            warehouse_id=warehouse.name,
                            pack_line=pack_line.name,
                            products=products_on_stock,
                            warehouse_costs=pack_line.cost_per_product * len(
                                products_on_stock),
                            shipment_costs=warehouse.cost_per_shipment,
                            order_datetime=order_datetime)
                    ])

        mono_pack_lines = warehouse.get_pack_lines('mono')
        for pack_line in mono_pack_lines:
            if self.capacity_tracker[(warehouse.name, pack_line.name)].is_available(
                    len(products_on_stock)):
                return (left_over_products, [
                    WarehouseOrder(
                        shop_order_id=order_id,
                        warehouse_id=warehouse.name,
                        pack_line=pack_line.name,
                        products=[product],
                        warehouse_costs=pack_line.cost_per_product,
                        shipment_costs=warehouse.cost_per_shipment,
                        order_datetime=order_datetime) for product in
                    products_on_stock])

        return products, []

    @staticmethod
    def select_cheapest_sourcing_option(sourcing_options: List[SourcingOption]):
        cheapest_sourcing_option = sourcing_options[0]
        for sourcing_option in sourcing_options[1:]:
            if sourcing_option.costs < cheapest_sourcing_option.costs:
                cheapest_sourcing_option = sourcing_option
        return cheapest_sourcing_option

    def source_order(self, order: DataFrame):
        sourcing_options = []
        product_ids = set(order['product_id'])
        order_id = order.order_id.iloc[0]
        order_datetime = order.datetime.iloc[0]

        warehouse_combinations = permutations(self.warehouses)

        for warehouse_combination in warehouse_combinations:
            products_to_be_sourced = product_ids
            warehouse_sourcing_options = []

            for warehouse in warehouse_combination:
                if products_to_be_sourced:
                    products_to_be_sourced, potential_warehouse_orders = \
                        self.create_sourcing_options(
                            products_to_be_sourced, warehouse, order_id, order_datetime)
                    warehouse_sourcing_options += potential_warehouse_orders

            sourcing_option = SourcingOption(
                warehouse_orders=warehouse_sourcing_options,
                lost_sales_shop_orders=LostSalesShopOrder(
                    shop_order_id=order_id,
                    order_datetime=order_datetime,
                    unsourceable_products=products_to_be_sourced)
            )

            if products_to_be_sourced:
                sourcing_option.penalty = self.lost_sales_penalty * len(
                    products_to_be_sourced)
            sourcing_options.append(sourcing_option)

        selected_sourcing_option = self.select_cheapest_sourcing_option(
            sourcing_options)

        self.capacity_tracker.update_capacity(selected_sourcing_option)
        return selected_sourcing_option
