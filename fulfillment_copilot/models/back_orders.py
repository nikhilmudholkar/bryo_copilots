from odoo import api, fields, models, tools
import pandas as pd


class BackOrdersView(models.Model):
    _name = "back.orders.view"
    _auto = False
    _description = "Back Orders Table Report"
    sale_order = fields.Char(string='sale_order')
    backorder_id = fields.Char(string='backorder_id')
    delivery_id = fields.Char(string='delivery_id')

    def create_table(self):
        self._cr.execute("""
        select sale_order.name as sale_order,
		table_1.backorder_id,
		table_1.picking_id as delivery_id
        FROM sale_order
        inner join (
            SELECT sale_id,
                    backorder_id,
                    picking_id,
                    table_1a.state,
                    table_1a.product_id,
                    table_1a.stock_movement_id,
                    table_1a.create_date,
                    table_1a.reserved_uom_qty,
                    table_1a.location_id,
                    table_1a.location_dest_id,
                    table_1a.product_uom_qty,
                    table_1a.write_date,
                    table_1a.qty_done
                FROM stock_picking
                inner join (
                    SELECT stock_move.picking_id,
                            stock_move.state,
                            stock_move.product_id, 	
                            stock_move.create_date,
                            stock_move.location_id,
                            stock_move.location_dest_id,
                            stock_move.id as stock_movement_id,
                            stock_move_line.reserved_uom_qty,
                            stock_move.product_uom_qty,
                            stock_move_line.write_date,
                            stock_move_line.qty_done
                        FROM stock_move
                        inner join stock_move_line
                        ON stock_move.id = stock_move_line.move_id)
                        AS table_1a
                ON stock_picking.id = table_1a.picking_id
                WHERE stock_picking.backorder_id notnull)
                AS table_1
        ON sale_order.id = table_1.sale_id""")
        # print("query fulfillment executed")
        result = self._cr.fetchall()
        columns = [desc[0] for desc in self._cr.description]
        df_table = pd.DataFrame(result, columns=columns)
        # print(df_table)

        if tools.table_exists(self._cr, "back_orders"):
            # print("table back_orders exists")
            self._cr.execute("""DROP TABLE back_orders CASCADE""")

        tools.create_model_table(self._cr, "back_orders", None, (("sale_order", "varchar", ""),
                                                                     ("backorder_id", "varchar", ""),
                                                                     ("delivery_id", "varchar", "")))
        # print("table stock_levels created")

        for index, row in df_table.iterrows():
            self._cr.execute("""INSERT INTO back_orders (sale_order, backorder_id, delivery_id) 
            VALUES (%s, %s, %s)""", (str(row['sale_order']),
                                     str(row['backorder_id']),
                                     str(row['delivery_id'])))

        return df_table

    @api.model
    def init(self):
        df_table = self.create_table()
        tools.drop_view_if_exists(self._cr, 'back_orders_view')
        self._cr.execute("""
                        CREATE OR REPLACE VIEW back_orders_view AS (
                        SELECT row_number() OVER () as id,
                            sale_order.name as sale_order,
                            table_1.backorder_id,
                            table_1.picking_id as delivery_id
                        FROM sale_order
                        inner join (
                            SELECT sale_id,
                                    backorder_id,
                                    picking_id,
                                    table_1a.state,
                                    table_1a.product_id,
                                    table_1a.stock_movement_id,
                                    table_1a.create_date,
                                    table_1a.reserved_uom_qty,
                                    table_1a.location_id,
                                    table_1a.location_dest_id,
                                    table_1a.product_uom_qty,
                                    table_1a.write_date,
                                    table_1a.qty_done
                                FROM stock_picking
                                inner join (
                                    SELECT stock_move.picking_id,
                                            stock_move.state,
                                            stock_move.product_id, 	
                                            stock_move.create_date,
                                            stock_move.location_id,
                                            stock_move.location_dest_id,
                                            stock_move.id as stock_movement_id,
                                            stock_move_line.reserved_uom_qty,
                                            stock_move.product_uom_qty,
                                            stock_move_line.write_date,
                                            stock_move_line.qty_done
                                        FROM stock_move
                                        inner join stock_move_line
                                        ON stock_move.id = stock_move_line.move_id)
                                        AS table_1a
                                ON stock_picking.id = table_1a.picking_id
                                WHERE stock_picking.backorder_id notnull)
                                AS table_1
                        ON sale_order.id = table_1.sale_id
                    )""")
