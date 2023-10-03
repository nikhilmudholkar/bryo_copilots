from odoo import api, fields, models, tools
import pandas as pd

class SaleOrderView(models.Model):
    _name = "sale.order.view"
    _auto = False
    _description = "Sale Order Table Report"
    sale_order = fields.Char(string='sale_order')
    # sale_order_id = fields.Float(string='Sale Order ID')
    # order_name = fields.
    ordered_date = fields.Datetime(string='ordered_date')
    due_date = fields.Datetime(string='due_date')
    created_by = fields.Integer(string='created_by')

    @api.model
    def init(self):
        tools.drop_view_if_exists(self._cr, 'sale_order_view')
        self._cr.execute("""
                CREATE OR REPLACE VIEW sale_order_view AS (
                    SELECT row_number() OVER () as id,
                        name as sale_order,
                        date_order as ordered_date,
                        commitment_date as due_date,
                        create_uid as created_by
                    FROM sale_order
                where state = 'sale')""")
        # print("query executed")
