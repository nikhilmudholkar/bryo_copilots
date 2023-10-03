from odoo import api, fields, models, tools
import pandas as pd

class StockLevelsView(models.Model):
    _name = "stock.levels.view"
    _auto = False
    _description = "Stock Levels Table Report"
    product_id = fields.Many2one('product.product', string='Product')
    stock_available = fields.Float(string='Quantity')
    reserved_quantity = fields.Float(string='Reserved Quantity')


    def create_table(self):
        self._cr.execute("""
                    SELECT product_id,
                        quantity as stock_available,
                        reserved_quantity
                    FROM stock_quant
                    WHERE inventory_date notnull
                    and product_id in (select product_id from sale_order_line)""")
        # print("query stock_levels executed")
        result = self._cr.fetchall()
        columns = [desc[0] for desc in self._cr.description]
        df_table = pd.DataFrame(result, columns=columns)
        # print(df_table)

        if tools.table_exists(self._cr, "stock_levels"):
            # print("table stock_levels exists")
            self._cr.execute("""DROP TABLE stock_levels CASCADE""")

        tools.create_model_table(self._cr, "stock_levels", None, (("product_id", "varchar", ""),
                                                                  ("stock_available", "varchar", ""),
                                                                  ("reserved_quantity", "varchar", "")))
        # print("table stock_levels created")

        for index, row in df_table.iterrows():
            self._cr.execute("""INSERT INTO stock_levels (product_id, stock_available, reserved_quantity) VALUES (%s, %s, %s)""",
                                            (str(row['product_id']), str(row['stock_available']), str(row['reserved_quantity'])))

        return df_table

    @api.model
    def init(self):
        df_table = self.create_table()
        tools.drop_view_if_exists(self._cr, 'stock_levels_view')
        self._cr.execute("""
                    CREATE OR REPLACE VIEW stock_levels_view AS (
                    SELECT row_number() OVER () as id,
                            product_id,
                            quantity as stock_available,
                            reserved_quantity
                        FROM stock_quant
                        WHERE inventory_date notnull
                        and product_id in (select product_id from sale_order_line))""")
        # print("query executed")
