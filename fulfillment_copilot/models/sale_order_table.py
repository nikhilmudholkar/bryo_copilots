import datetime
import json

import requests

from odoo import api, fields, models, tools
import pandas as pd
# from utils import create_llm_prompt
from .create_llm_prompt import create_llm_message, askai



class OpenSaleOrderView(models.Model):
    _name = "open.sale.order.table.report"
    _auto = False
    _description = "Open Sale Order Table Report"
    order_id = fields.Char(string='Sale Order ID')
    # sale_order_id = fields.Float(string='Sale Order ID')
    # order_name = fields.
    time_to_deliver = fields.Char(string='time_to_deliver')
    # time_to_create_delivery_order = fields.Char(string='time_to_create_delivery_order')
    # time_to_pick = fields.Char(string='time_to_pick')


    # @api.model
    def getdata(self):
        # print(f"Inside get data")
        # tools.drop_view_if_exists(self._cr, 'sale_order_table_report')
        # filter this query to only select records where delivery_status = 'pending' in sale_order
        # self._cr.execute("""SELECT id, date_order, create_uid, state FROM sale_order""")

        # table 1
        self._cr.execute("""            
                        SELECT name as sale_order,
                            date_order as ordered_date,
                            commitment_date as due_date,
                            create_uid as created_by
                        FROM sale_order
                    """)
        # print("table 1 query executed")
        result = self._cr.fetchall()
        columns = [desc[0] for desc in self._cr.description]
        df_table1 = pd.DataFrame(result, columns=columns)
        # print(df_table1)


        # table 2
        self._cr.execute("""
                SELECT sale_order.name as order,
                    product_id,
                    product_uom_qty as ordered_quantity
                FROM sale_order
                inner join sale_order_line
                ON sale_order.id = sale_order_line.order_id
                where sale_order.state = 'sale' 
        """)
        # print("table 2 query executed")
        result = self._cr.fetchall()
        columns = [desc[0] for desc in self._cr.description]
        df_table2 = pd.DataFrame(result, columns=columns)
        # print(df_table2)

        # if tools.table_exists(self._cr, "ordered_products"):
        #     print("table exists")
        #     self._cr.execute("""DROP TABLE ordered_products CASCADE""")
        #
        # tools.create_model_table(self._cr, "ordered_products", None, (("order", "varchar", ""),
        #                                                             ("product_id", "varchar", ""),
        #                                                             ("product_uom_qty", "varchar", "")))
        # for index, row in df_table2.iterrows():
        #     self._cr.execute("""INSERT INTO ordered_products (order, product_id, product_uom_qty) VALUES (%s, %s, %s)""",(str(row['order']), str(row['product_id']), str(row['ordered_quantity'])))

        

        # table 4
        self._cr.execute("""
                SELECT sale_order.name as sale_order,
                stock_picking.id as delivery_id,
                stock_picking.state as delivery_state,
                stock_picking.create_date, 
                stock_picking.date_deadline as committed_date,
                stock_picking.scheduled_date,
                stock_picking.date_done as delivered_date,
                stock_picking.priority as delivery_priority
            FROM sale_order
            inner join stock_picking
            ON sale_order.id = stock_picking.sale_id
""")
        # print("table 4 query executed")
        result = self._cr.fetchall()
        columns = [desc[0] for desc in self._cr.description]
        df_table4 = pd.DataFrame(result, columns=columns)
        # print(df_table4.columns)

        

        # Time to deliver: DIFF (ORDERED_DATE, if all stock_picking.id related to the order have a date_done, then MAX(DATE_DONE), otherwise current date)


        # for a unique order in table 1, get all the rows with same order in table 4 and get the maximum date_done timestamp amongst those
        # get all unique orders in df_table_4
        # orders = df_table4['sale_order'].unique()
        # check if all the stock_picking.id related to the order have a date_done

        # for order in orders:
        #     # get all the stock_picking.id related to the order
        #     stock_picking_ids = df_table4[df_table4['sale_order'] == order]['delivery_id']
        #     # check if all the stock_picking.id related to the order have a date_done
        #     if df_table4[df_table4['delivery_id'].isin(stock_picking_ids)]['delivered_date'].isnull().values.any():
        #         # if any of the stock_picking.id related to the order have a null date_done, then set the date_done to current date
        #         df_table4.loc[df_table4['sale_order'] == order, 'delivered_date'] = datetime.datetime.now()
        #     else:
        #         # if all the stock_picking.id related to the order have a date_done, then set the date_done to max(date_done)
        #         df_table4.loc[df_table4['sale_order'] == order, 'delivered_date'] = df_table4[df_table4['delivery_id'].isin(stock_picking_ids)]['delivered_date'].max()

        # df_table4_max_dates = df_table4.groupby('order').agg({'date_done': 'max'}).reset_index()

        # # do the same thing as above for create_date and append the new column to df_table4_max_dates
        # df_table4['create_date'] = df_table4.groupby('sale_order').agg({'create_date': 'max'}).reset_index()[
        #     'create_date']

        # now for every order in table 4, get the corresponding ordered_date from table 1 and calculate difference between date_done and ordered_date
        df_table_merged = df_table4.merge(df_table1, on='sale_order', how='left')

        # df_table_merged['time_to_deliver'] = df_table_merged['delivered_date'] - df_table_merged['ordered_date']
        # if all stock_picking.id related to the order have a date_done, then MAX(DATE_DONE), otherwise current date)

        # df_table_merged['time_to_create_delivery_order'] = df_table_merged['create_date'] - df_table_merged[
        #     'ordered_date']


        # # table 5
        # self._cr.execute("""
        #                 select sale_order.name as sale_order,
        #             table_1.state,
        #             table_1.stock_movement_id,
        #             table_1.backorder_id,
        #             table_1.product_id,
        #             table_1.product_uom_qty,
        #             table_1.reserved_uom_qty,
        #             table_1.qty_done,
        #             table_1.write_date,
        #             table_1.location_id
        #         FROM sale_order
        #         inner join (
        #             SELECT sale_id,
        #                     backorder_id,
        #                     table_1a.state,
        #                     table_1a.product_id,
        #                     table_1a.stock_movement_id,
        #                     table_1a.reserved_uom_qty,
        #                     table_1a.location_id,
        #                     table_1a.product_uom_qty,
        #                     table_1a.write_date,
        #                     table_1a.qty_done
        #                 FROM stock_picking
        #                 inner join (
        #                     SELECT stock_move.picking_id,
        #                             stock_move.state,
        #                             stock_move.product_id,
        #                             stock_move_line.id as stock_movement_id,
        #                             stock_move_line.reserved_uom_qty,
        #                             stock_move_line.location_id,
        #                             stock_move.product_uom_qty,
        #                             stock_move_line.write_date,
        #                             stock_move_line.qty_done
        #                         FROM stock_move
        #                         inner join stock_move_line
        #                         ON stock_move.id = stock_move_line.move_id)
        #                         AS table_1a
        #                 ON stock_picking.id = table_1a.picking_id )
        #                 AS table_1
        #         ON sale_order.id = table_1.sale_id
        #         where sale_order.state = 'sale'
        #             """)
        # # print("table 5 query executed")
        # result = self._cr.fetchall()
        # columns = [desc[0] for desc in self._cr.description]
        # df_table5 = pd.DataFrame(result, columns=columns)
        #
        # # filter table 5 to only get records where state = 'done'
        # df_table5 = df_table5[df_table5['state'] == 'done']
        # # for a unique order, get all the rows with same order in table 5 and get the maximum write_date timestamp amongst those
        # df_table5_max_dates = df_table5.groupby('sale_order').agg({'write_date': 'max'}).reset_index()
        # # print(df_table5_max_dates)
        #
        # # for every order in df_table5_max_dates, get the corresponding create_date from df_table_merged and calculate difference between write_date and create_date
        # df_table_merged = df_table_merged.merge(df_table5_max_dates, on='sale_order', how='left')
        # df_table_merged['time_to_pick'] = df_table_merged['write_date'] - df_table_merged['create_date']

        #         print data in all the columns of df_table_merged
        # df_table_merged = df_table_merged[['sale_order', 'time_to_deliver', 'time_to_create_delivery_order', 'time_to_pick']]
        # df_table_merged = df_table_merged[['sale_order', 'time_to_deliver']]
        df_table_merged = df_table_merged[['sale_order']]
        # print(df_table_merged)


        if tools.table_exists(self._cr, "order_tracking"):
            # print("table exists")
            self._cr.execute("""DROP TABLE order_tracking CASCADE""")

        tools.create_model_table(self._cr, "order_tracking", None, (("index", "varchar", ""),
                                                                    ("order_id", "varchar", ""),
                                                                    # ("time_to_deliver", "varchar", ""),
                                                                    # ("time_to_create_delivery_order", "varchar", ""),
                                                                    # ("time_to_pick", "varchar", "")))
                                                                    ))
        for index, row in df_table_merged.iterrows():
            # print(row['sale_order'])
            # self._cr.execute("""INSERT INTO order_tracking (order_id, time_to_deliver, time_to_create_delivery_order, time_to_pick) VALUES (%s, %s, %s, %s)""",
            #                  (str(row['sale_order']), str(row['time_to_deliver']), str(row['time_to_create_delivery_order']), str(row['time_to_pick'])))
            # self._cr.execute("""INSERT INTO order_tracking (order_id, time_to_deliver) VALUES (%s, %s)""",
                             # (str(row['sale_order']), str(row['time_to_deliver'])))
            self._cr.execute("""INSERT INTO order_tracking (index, order_id) VALUES (%s,%s)""",
                             (str(index), str(row['sale_order'])))

        return df_table_merged


    @api.model
    def init(self):
        # print("query execution started")
        df_final = self.getdata()
        tools.drop_view_if_exists(self._cr, 'open_sale_order_table_report')
        # self._cr.execute("""
        #     CREATE OR REPLACE VIEW open_sale_order_table_report AS (
        #     SELECT row_number() OVER () as id,
        #         so.order_id AS order_id,
        #         so.time_to_deliver as time_to_deliver,
        #         so.time_to_create_delivery_order as time_to_create_delivery_order,
        #         so.time_to_pick as time_to_pick
        #     FROM order_tracking so )""")
        # self._cr.execute("""CREATE OR REPLACE VIEW open_sale_order_table_report AS (
        #      SELECT row_number() OVER () as id,
        #          so.order_id AS order_id,
        #          so.time_to_deliver as time_to_deliver
        #      FROM order_tracking so )""")
        self._cr.execute("""CREATE OR REPLACE VIEW open_sale_order_table_report AS (
                     SELECT row_number() OVER () as id,
                         so.order_id AS order_id
                     FROM order_tracking so )""")
        # print("query executed")

        # print(df_final)



    def triggerllm(self, context=None):
        # print(self.env.context)
        active_index_ids = self.env.context['active_ids']
        # print(active_index_ids)

        self._cr.execute("""SELECT order_id FROM order_tracking where id in %s""", (tuple(active_index_ids),))
        result = self._cr.fetchall()
        order_ids = [row[0] for row in result]
        # print(order_ids)
        # order_ids = [order_ids]
        result_dict = {}
        for order_id in order_ids:

            # get sale_order
            self._cr.execute("""SELECT name as sale_order,
                                    date_order as ordered_date,
                                    commitment_date as due_date,
                                    create_uid as created_by
                                FROM sale_order
                                where state = 'sale' and  name = %s""", (order_id,))
            result = self._cr.fetchall()
            columns = [desc[0] for desc in self._cr.description]
            df_sale_order = pd.DataFrame(result, columns=columns)

            # strip the time from all the datetime columns. These columns are in string format so convert them to
            # string first convert the datetime columns to strings
            df_sale_order['ordered_date'] = df_sale_order['ordered_date'].astype(str)
            df_sale_order['ordered_date'] = df_sale_order['ordered_date'].str[:10]
            # df_sale_order['ordered_date'] = df_sale_order['ordered_date'].dt.date
            df_sale_order['due_date'] = df_sale_order['due_date'].astype(str)
            df_sale_order['due_date'] = df_sale_order['due_date'].str[:10]
            # print datatype of all the columns
            # print(df_sale_order.dtypes)


            # get ordered_products table
            self._cr.execute("""SELECT sale_order, 
                                        product_id, 
                                        ordered_quantity 
                                FROM ordered_products where sale_order = %s""",
                             (order_id,))
            result = self._cr.fetchall()
            columns = [desc[0] for desc in self._cr.description]
            df_ordered_products = pd.DataFrame(result, columns=columns)


            # get fulfillment table
            self._cr.execute("""SELECT sale_order, delivery_id, delivery_state, committed_date,
                                scheduled_date, delivered_date, delivery_priority from fulfillment where sale_order = %s""", (order_id,))
            result = self._cr.fetchall()
            columns = [desc[0] for desc in self._cr.description]
            df_fulfillment = pd.DataFrame(result, columns=columns)

            # strip the time from all the datetime columns
            # convert the datetime columns to strings
            # df_fulfillment['fulfillment_create_date'] = df_fulfillment['fulfillment_create_date'].astype(str)
            # df_fulfillment['fulfillment_create_date'] = df_fulfillment['fulfillment_create_date'].str[:10]
            df_fulfillment['committed_date'] = df_fulfillment['committed_date'].astype(str)
            df_fulfillment['committed_date'] = df_fulfillment['committed_date'].str[:10]
            df_fulfillment['scheduled_date'] = df_fulfillment['scheduled_date'].astype(str)
            df_fulfillment['scheduled_date'] = df_fulfillment['scheduled_date'].str[:10]
            df_fulfillment['delivered_date'] = df_fulfillment['delivered_date'].astype(str)
            df_fulfillment['delivered_date'] = df_fulfillment['delivered_date'].str[:10]
            # print(df_fulfillment.dtypes)

            # get stock_movements table
            self._cr.execute("""SELECT sale_order, delivery_id, stock_picking_id, picking_state, picking_create_date, 
                                product_id, picking_order_quantity, reserved_quantity, picked_quantity, picking_write_date,
                                stock_picking_origin, stock_picking_destination from stock_movements where sale_order = %s""", (order_id,))
            result = self._cr.fetchall()
            columns = [desc[0] for desc in self._cr.description]
            df_stock_movements = pd.DataFrame(result, columns=columns)

            # strip the time from all the datetime columns
            # convert the datetime columns to strings
            df_stock_movements['picking_create_date'] = df_stock_movements['picking_create_date'].astype(str)
            df_stock_movements['picking_create_date'] = df_stock_movements['picking_create_date'].str[:10]
            df_stock_movements['picking_write_date'] = df_stock_movements['picking_write_date'].astype(str)
            df_stock_movements['picking_write_date'] = df_stock_movements['picking_write_date'].str[:10]
            # print(df_stock_movements.dtypes)


            # get back_orders table
            self._cr.execute("""SELECT sale_order, backorder_id, delivery_id from back_orders where sale_order = %s""", (order_id,))
            result = self._cr.fetchall()
            columns = [desc[0] for desc in self._cr.description]
            df_back_orders = pd.DataFrame(result, columns=columns)


            # message = create_llm_message(df_sale_order, df_ordered_products, df_fulfillment, df_stock_movements)


        # url = "http://35.92.128.67:8000/askai"
        # payload for slack webhook endpoint to send messages to a channel
        # payload = {
        #     "question": "Q: Who is elon musk? A: ",
        #     "max_tokens": 100,
        #     "stop": ["Q:", "\n"],
        #     "security_token": "bryo_access_control_1",
        #     # "echo": "true"
        # }

            response_palm = str(order_id) + "\n"
            llm_result = askai(df_sale_order, df_ordered_products, df_fulfillment, df_stock_movements, df_back_orders)
            response_palm = response_palm + llm_result

            # insert order_id, llm_result and current datetime into copilot_suggestions table
            self._cr.execute("INSERT INTO copilot_suggestions (sales_order_id, recommendation, recommendation_time) VALUES (%s, %s, %s)", (str(order_id), str(llm_result), str(datetime.datetime.now())))

            # response_palm = response_palm.replace("\n", "<br>")
            url_slack = "https://hooks.slack.com/services/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"
            # payload for slack webhook endpoint to send messages to a channel
            slack_data = {'text': response_palm}

            # print(slack_data)
            # print(response_llama.text)
            # print(type(slack_data))
            # print(str(response_llama.text))
            response = requests.post(
                url_slack, data=json.dumps(slack_data),
                headers={'Content-Type': 'application/json'}
            )
            # print(response.text)
            message = response_palm
            # print(self.env['mail.channel'].search([('name', '=', "Bryo copilot suggestions")]).id)
            if self.env['mail.channel'].search([('name', '=', "Bryo copilot suggestions")]).id:
                channel_id = self.env['mail.channel'].search([('name', '=', "Bryo copilot suggestions")]).id
                # print(channel_id)
                self.env['mail.channel'].browse(channel_id).message_post(body=message, message_type='comment')