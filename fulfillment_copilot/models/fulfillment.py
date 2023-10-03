from odoo import api, fields, models, tools
import pandas as pd

class FulfillmentView(models.Model):
    _name = "fulfillment.view"
    _auto = False
    _description = "Stock Levels Table Report"
    sale_order = fields.Char(string='sale_order')
    delivery_id = fields.Float(string='delivery_id')
    delivery_state = fields.Char(string='delivery_state')
    # fulfillment_create_date = fields.Datetime(string='fulfillment_create_date')
    committed_date = fields.Datetime(string='committed_date')
    scheduled_date = fields.Datetime(string='scheduled_date')
    delivered_date = fields.Datetime(string='delivered_date')
    delivery_priority = fields.Char(string='delivery_priority')


    def create_table(self):
        self._cr.execute("""
                    SELECT sale_order.name as sale_order,
                        stock_picking.id as delivery_id,
                        stock_picking.state as delivery_state,
                        stock_picking.date_deadline as committed_date,
                        stock_picking.scheduled_date,
                        stock_picking.date_done as delivered_date,
                        stock_picking.priority as delivery_priority
                    FROM sale_order
                    inner join stock_picking
                    ON sale_order.id = stock_picking.sale_id
                """)
        # print("query fulfillment executed")
        result = self._cr.fetchall()
        columns = [desc[0] for desc in self._cr.description]
        df_table = pd.DataFrame(result, columns=columns)
        # print(df_table)

        if tools.table_exists(self._cr, "fulfillment"):
            # print("table fulfillment exists")
            self._cr.execute("""DROP TABLE fulfillment CASCADE""")

        tools.create_model_table(self._cr, "fulfillment", None, (("sale_order", "varchar", ""),
                                                                  ("delivery_id", "varchar", ""),
                                                                  ("delivery_state", "varchar", ""),
                                                                  # ("fulfillment_create_date", "varchar", ""),
                                                                  ("committed_date", "varchar", ""),
                                                                  ("scheduled_date", "varchar", ""),
                                                                  ("delivered_date", "varchar", ""),
                                                                  ("delivery_priority", "varchar", "")))
        # print("table stock_levels created")

        for index, row in df_table.iterrows():
            self._cr.execute("""INSERT INTO fulfillment (sale_order, delivery_id, delivery_state, committed_date, scheduled_date, delivered_date, delivery_priority) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",(str(row['sale_order']),
                                                    str(row['delivery_id']),
                                                    str(row['delivery_state']),
                                                    # str(row['fulfillment_create_date']),
                                                    str(row['committed_date']),
                                                    str(row['scheduled_date']),
                                                    str(row['delivered_date']),
                                                    str(row['delivery_priority'])))

        return df_table

    @api.model
    def init(self):
        df_table = self.create_table()
        tools.drop_view_if_exists(self._cr, 'fulfillment_view')
        self._cr.execute("""
                    CREATE OR REPLACE VIEW fulfillment_view AS (
                    SELECT row_number() OVER () as id,
                            sale_order.name as sale_order,
                            stock_picking.id as delivery_id,
                            stock_picking.state as delivery_state,
                            stock_picking.date_deadline as committed_date,
                            stock_picking.scheduled_date,
                            stock_picking.date_done as delivered_date,
                            stock_picking.priority as delivery_priority
                    FROM sale_order
                    inner join stock_picking
                    ON sale_order.id = stock_picking.sale_id)""")
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
        # get user id
        # self.user = self.env['res.users'].search([('id', '=', self.env.uid)])
        # get channel id
        # self.channel_id = self.env['mail.channel'].search([('name', '=', 'channel_bryo_copilot')])
        # notification_ids = [((0, 0, {
        #     'res_partner_id': self.user.partner_id.id,
        #     'notification_type': 'inbox'}))]
        # user_id = self.env.user.id
        # message = ("You have a assigned a task")
        # channel_id.message_post(author_id=user_id,
        #                         body=(message),
        #                         message_type='notification',
        #                         subtype_xmlid="mail.mt_comment",
        #                         notification_ids=notification_ids,
        #                         partner_ids=[self.user.id],
        #                         notify_by_email=False,
        #                         )

        message = 'The AI copilot is now active!'
        # print(self.env['mail.channel'].search([('name', '=', "Bryo copilot suggestions")]).id)
        if self.env['mail.channel'].search([('name', '=', "Bryo copilot suggestions")]).id:
            channel_id = self.env['mail.channel'].search([('name', '=', "Bryo copilot suggestions")]).id
            # print(channel_id)
            self.env['mail.channel'].browse(channel_id).message_post(body=message, message_type='comment')

