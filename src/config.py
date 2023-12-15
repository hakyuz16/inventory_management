warehouses = [
    {"name": "warehouseA",
     "pack_lines": [
         {"name": "monoManual",
          "type": "mono",
          "capacity": 100,
          "cost_per_product": 0.7},
         {"name": "multiManual",
          "type": "multi",
          "capacity": 200,
          "cost_per_product": 0.9}
     ],
     "cost_per_shipment": 5,
     "stock_capacity": 600
     },
    {"name": "warehouseB",
     "pack_lines": [
         {"name": "monoManual",
          "type": "mono",
          "capacity": 300,
          "cost_per_product": 0.5},
         {"name": "multiManual",
          "type": "multi",
          "capacity": 200,
          "cost_per_product": 0.7}
     ],
     "cost_per_shipment": 6,
     "stock_capacity": 600
     }
]

LOST_SALES_PENALTY = 10.0
