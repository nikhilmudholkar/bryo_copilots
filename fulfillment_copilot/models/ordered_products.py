from odoo import api, fields, models, tools
import pandas as pd

class OrderedProductsView(models.Model):
    _name = "ordered.products.view"
    _auto = False
    _description = "Ordered Products Table Report"
    sale_order = fields.Char(string='sale_order')
    product_id = fields.Many2one('product.product', string='Product')
    ordered_quantity = fields.Float(string='Ordered Quantity')


    def create_table(self):
        self._cr.execute("""
                    SELECT sale_order.name as sale_order,
                        product_id,
                        product_uom_qty as ordered_quantity
                    FROM sale_order
                    inner join sale_order_line
                    ON sale_order.id = sale_order_line.order_id
                    where sale_order.state = 'sale'""")
        # print("query executed")
        result = self._cr.fetchall()
        columns = [desc[0] for desc in self._cr.description]
        df_table = pd.DataFrame(result, columns=columns)
        # print(df_table)

        if tools.table_exists(self._cr, "ordered_products"):
            # print("table ordered_products exists")
            self._cr.execute("""DROP TABLE ordered_products CASCADE""")

        tools.create_model_table(self._cr, "ordered_products", None, (("sale_order", "varchar", ""),
                                                                        ("product_id", "varchar", ""),
                                                                        ("ordered_quantity", "varchar", "")))
        # print("table ordered_products created")

        for index, row in df_table.iterrows():
            self._cr.execute("""INSERT INTO ordered_products (sale_order, product_id, ordered_quantity) VALUES (%s, %s, %s)""",
                                            (str(row['sale_order']), str(row['product_id']), str(row['ordered_quantity'])))

        return df_table

    @api.model
    def init(self):
        df_table = self.create_table()
        tools.drop_view_if_exists(self._cr, 'ordered_products_view')
        self._cr.execute("""
                    CREATE OR REPLACE VIEW ordered_products_view AS (
                    SELECT row_number() OVER () as id,
                            sale_order.name as sale_order,
                            product_id,
                            product_uom_qty as ordered_quantity
                        FROM sale_order
                        inner join sale_order_line
                        ON sale_order.id = sale_order_line.order_id
                        where sale_order.state = 'sale'
)""")
        # print("query executed")
