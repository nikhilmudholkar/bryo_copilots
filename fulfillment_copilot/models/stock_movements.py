from odoo import api, fields, models, tools
import pandas as pd

class StockMovementsView(models.Model):
    _name = "stock.movements.view"
    _auto = False
    _description = "Stock Movements Table Report"
    sale_order = fields.Char(string='sale_order')
    delivery_id = fields.Float(string='delivery_id')
    stock_picking_id = fields.Float(string='stock_picking_id')
    picking_state = fields.Char(string='picking_state')
    picking_create_date = fields.Datetime(string='picking_create_date')
    product_id = fields.Many2one('product.product', string='Product_id')
    picking_order_quantity = fields.Float(string='picking_order_quantity')
    reserved_quantity = fields.Float(string='reserved_quantity')
    picked_quantity = fields.Float(string='picked_quantity')
    picking_write_date = fields.Datetime(string='picking_write_date')
    stock_picking_origin = fields.Many2one('stock.location', string='stock_picking_origin')
    stock_picking_destination = fields.Many2one('stock.location', string='stock_picking_destination')


    def create_table(self):
        self._cr.execute("""
                    select sale_order.name as sale_order,
                    table_1.picking_id as delivery_id,
                    table_1.stock_movement_id as stock_picking_id,
                    table_1.state as picking_state,
                    table_1.create_date as picking_create_date,
                    table_1.product_id,
                    table_1.product_uom_qty as picking_order_quantity,
                    table_1.reserved_uom_qty as reserved_quantity,
                    table_1.qty_done as picked_quantity,
                    table_1.write_date as picking_write_date,
                    table_1.location_id as stock_picking_origin,
                    table_1.location_dest_id as stock_picking_destination
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
                        ON stock_picking.id = table_1a.picking_id )
                        AS table_1
                ON sale_order.id = table_1.sale_id""")
        # print("query fulfillment executed")
        result = self._cr.fetchall()
        columns = [desc[0] for desc in self._cr.description]
        df_table = pd.DataFrame(result, columns=columns)
        # print(df_table)

        if tools.table_exists(self._cr, "stock_movements"):
            # print("table stock_movements exists")
            self._cr.execute("""DROP TABLE stock_movements CASCADE""")

        tools.create_model_table(self._cr, "stock_movements", None, (("sale_order", "varchar", ""),
                                                                     ("delivery_id", "varchar", ""),
                                                                     ("stock_picking_id", "varchar", ""),
                                                                     ("picking_state", "varchar", ""),
                                                                     ("picking_create_date", "varchar", ""),
                                                                     ("product_id", "varchar", ""),
                                                                     ("picking_order_quantity", "varchar", ""),
                                                                     ("reserved_quantity", "varchar", ""),
                                                                     ("picked_quantity", "varchar", ""),
                                                                     ("picking_write_date", "varchar", ""),
                                                                     ("stock_picking_origin", "varchar", ""),
                                                                     ("stock_picking_destination", "varchar", "")))
        # print("table stock_levels created")

        for index, row in df_table.iterrows():
            self._cr.execute("""INSERT INTO stock_movements (sale_order, delivery_id, stock_picking_id, picking_state, picking_create_date, product_id, picking_order_quantity, reserved_quantity, picked_quantity, picking_write_date, stock_picking_origin, stock_picking_destination) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",(str(row['sale_order']),
                                                            str(row['delivery_id']),
                                                            str(row['stock_picking_id']),
                                                            str(row['picking_state']),
                                                            str(row['picking_create_date']),
                                                            str(row['product_id']),
                                                            str(row['picking_order_quantity']),
                                                            str(row['reserved_quantity']),
                                                            str(row['picked_quantity']),
                                                            str(row['picking_write_date']),
                                                            str(row['stock_picking_origin']),
                                                            str(row['stock_picking_destination'])))

        return df_table

    @api.model
    def init(self):
        df_table = self.create_table()
        tools.drop_view_if_exists(self._cr, 'stock_movements_view')
        self._cr.execute("""
                    CREATE OR REPLACE VIEW stock_movements_view AS (
                    SELECT row_number() OVER () as id,
                            sale_order.name as sale_order,
                    table_1.picking_id as delivery_id,
                    table_1.stock_movement_id as stock_picking_id,
                    table_1.state as picking_state,
                    table_1.create_date as picking_create_date,
                    table_1.product_id,
                    table_1.product_uom_qty as picking_order_quantity,
                    table_1.reserved_uom_qty as reserved_quantity,
                    table_1.qty_done as picked_quantity,
                    table_1.write_date as picking_write_date,
                    table_1.location_id as stock_picking_origin,
                    table_1.location_dest_id as stock_picking_destination
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
                        ON stock_picking.id = table_1a.picking_id )
                        AS table_1
                ON sale_order.id = table_1.sale_id)""")
        # self._cr.execute("""
        #             CREATE OR REPLACE VIEW fulfillment_view AS (
        #             SELECT row_number() OVER () as id,
        #                     order_id,
        #                     state,
        #                     create_date,
        #                     date_deadline,
        #                     scheduled_date,
        #                     date_done,
        #                     priority
        #                 FROM fulfillment)""")
        # print("query executed")
