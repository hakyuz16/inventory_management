from pandas import DataFrame
from .order_sourcing import OrderSourcer
from .config import warehouses, LOST_SALES_PENALTY
from .models import SimulationResult


def simulate(orders: DataFrame, stock_allocation: DataFrame) -> SimulationResult:
    warehouse_orders = []
    order_sourcer = OrderSourcer(stock_allocation, warehouses, LOST_SALES_PENALTY)

    for day, day_orders in orders.groupby(orders.datetime.dt.date):
        for orderId, order in day_orders.groupby('order_id'):
            warehouse_orders.append(order_sourcer.source_order(order))

        order_sourcer.capacity_tracker.reset_capacities()
    return SimulationResult(warehouse_orders)
