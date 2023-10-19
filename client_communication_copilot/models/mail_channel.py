import base64
# import json
import re
from datetime import datetime

import pandas as pd

import odoo
from odoo import api, fields, models, _
from .create_llm_prompt import remove_tags, uploadpdftollm, identify_client, identify_sale_orders
from odoo.exceptions import UserError
from .track_sale_orders import track_sale_orders

class Channel(models.Model):
    # added test comment
    _inherit = 'mail.channel'
    process_tracker = fields.Char(string="Process Tracker", default="process_started")
    unstructured_data = fields.Char(string="Unstructured Data", default="unstructured_data")
    unstructured_data_formatted = fields.Char(string="Unstructured Data Formatted", default="unstructured_data_formatted")
    ai_message = fields.Char(string="AI Message", default="")
    client_id = fields.Char(string="Client ID", default="client_id")
    # create a variable to store array called order_ids
    order_ids = fields.Char(string="Order IDs", default="order_ids")
    so_filters = fields.Char(string="SO Filters", default="so_filters")
    sale_order_revert = fields.Char(string="Sale Order Revert", default="")
    sale_order_line_revert = fields.Char(string="Sale Order Line Revert", default="")
    original_sale_order = fields.Many2one('sale.order', string="Original Sale Order")
    original_sale_order_line = fields.Many2one('sale.order.line', string="Original Sale Order Line")


    def save_orignal_sale_order(self, sale_order_id):
        sale_order = self.env['sale.order'].search([
            ('id', '=', sale_order_id)
        ])[0]
        original_values = sale_order.read()[0]
        self.sale_order_revert = str(original_values)


    def save_orignal_sale_order_line(self, sale_order_id, product_id):
        sale_order_line = self.env['sale.order.line'].search([
            ('order_id', '=', sale_order_id),
            ('product_id', '=', product_id)
        ])[0]
        print(sale_order_line.read()[0])
        original_values = sale_order_line.read()[0]
        self.sale_order_line_revert = self.sale_order_line_revert + "\n" + str(original_values)



    def update_sale_order_line(self, sale_order_id, product_id, field_name, new_value):
        sale_order = self.env['sale.order.line'].search([
            ('order_id', '=', sale_order_id),
            ('product_id', '=', product_id)
        ])[0]
        original_values = sale_order.read()[0]
        sale_order[field_name] = new_value
        sale_order.write({})

    def update_stock_picking(self, stock_picking_id, product_id, field_name, new_value):
        stock_picking = self.env['stock.picking'].search([
            ('id', '=', stock_picking_id),
            ('product_id', '=', product_id)
        ])[0]
        original_values = stock_picking.read()[0]
        stock_picking[field_name] = new_value
        stock_picking.write({})

    def update_sale_order(self, sale_order_id, field_name, new_value):
        sale_order = self.env['sale.order'].search([
            ('id', '=', sale_order_id)
        ])[0]
        original_values = sale_order.read()[0]
        sale_order[field_name] = new_value
        sale_order.write({})

    def revert_sale_order_values(sale_order, original_values):
        for key in original_values.keys():
            sale_order[key] = original_values[key]
        sale_order.write({})



        # sale_order.save()
    # this method in all the apps (client_communication_copilot and lead_time_copilot) is called when a message is posted in any channel
    def _notify_thread(self, message, msg_vals=False, json=None, **kwargs):
        # print("message", message)
        if self.process_tracker == 'process_completed':
            self.process_tracker = 'process_started'
        rdata = super(Channel, self)._notify_thread(message, msg_vals=msg_vals, **kwargs)
        # bard_suggestions_channel = self.env.ref('lead_time_copilot.channel_bard_suggestions')
        bryo_channels = self.env['mail.channel'].search([('name', 'ilike', '%Client%')])
        bryo_channel_ids = [channel.id for channel in bryo_channels]
        copilot_user = self.env.ref("client_communication_copilot.copilot_user")
        partner_copilot = self.env.ref("client_communication_copilot.client_copilot_user_partner")
        author_id = msg_vals.get('author_id')
        copilot_name = str(partner_copilot.name or '') + ', '
        res = ""
        res_df = pd.DataFrame()

        if author_id != partner_copilot.id and msg_vals.get('model', '') == 'mail.channel' and msg_vals.get('res_id',
                                                                                                            0) in bryo_channel_ids:
            odoo_bot_user = self.env.ref("base.user_root")
            messages = self.message_ids
            latest_message = remove_tags(messages[0].body)
            latest_author_id = messages[0].author_id.id
            latest_channel_name = messages[0].record_name
            latest_channel = self.env['mail.channel'].search([('name', '=', latest_channel_name)])
            latest_message_attachment = messages[0].attachment_ids
            if latest_message_attachment:
                attachment = latest_channel.message_ids.mapped('attachment_ids')[0]
                # print("Attachment is present")
                pdf_file = base64.decodebytes(attachment.datas)
                # with open(
                #         '/Users/nikhilmukholdar/Personal/fintel_labs/odoo_global/odoo/dev/lead_time_copilot/my_pdf_file_clients.pdf',
                #         'wb') as f:
                #     f.write(pdf_file)
                # response = uploadpdftollm(
                #     '/Users/nikhilmukholdar/Personal/fintel_labs/odoo_global/odoo/dev/lead_time_copilot/my_pdf_file_clients.pdf')

                with open(
                        '/opt/odoo/odoo16/addons/client_communication_copilot/my_pdf_file.pdf',
                        'wb') as f:
                    f.write(pdf_file)
                response = uploadpdftollm(
                    '/opt/odoo/odoo16/addons/client_communication_copilot/my_pdf_file.pdf')


                # latest_channel.with_user(copilot_user).message_post(body=response, message_type='comment',
                #                                                     subtype_xmlid='mail.mt_comment')
                # response = response.replace('\n', ' ')
                # self.unstructured_data = response
                # self.process_tracker = 'identify_vendor'
                latest_message = response
                print(latest_message)
                # convert response to html
                # response = response.replace('\n', '<br/>')
                # response = '<p>' + response + '</p>'
                # latest_channel.with_user(copilot_user).message_post(body=response, message_type='comment',
                #                                                     subtype_xmlid='mail.mt_comment')

                self.unstructured_data = response
                # print("response from mail_channel_clients.py", self.unstructured_data_clients)
                self.process_tracker = 'identify_client'

            if self.process_tracker == 'process_started':
                print("Inside process started")
                print(self.process_tracker)
                self.process_tracker = 'identify_client'
                self.unstructured_data = latest_message
                self.unstructured_data_formatted = messages[0].body
                # replace <br> with \n
                self.unstructured_data_formatted = self.unstructured_data_formatted.replace("<br>", "\n")
                self.unstructured_data_formatted = self.unstructured_data_formatted.replace("<p>", "")
                self.unstructured_data_formatted = self.unstructured_data_formatted.replace("</p>", "")
                print("LATEST MESSAGE: ", self.unstructured_data_formatted)
                self.unstructured_data = self.unstructured_data_formatted
                print(self.unstructured_data)

            if latest_message == "exit":
                print("INSIDE EXIT")
                self.process_tracker = 'process_completed'
                self.unstructured_data = ''
                self.latest_ai_response = ''
                self.vendor_id = ''
                self.product_ids = ''
                self.ai_message = ''
                self.purchase_orders = ''
                self.rfq = False
                self.sale_order_revert = ""
                self.sale_order_line_revert = ""

                print("process completed")

            if self.process_tracker == 'identify_client':
                if latest_message.lower() != "yes" and messages[0].author_id.name not in ['OdooBot', 'Copilot']:
                    self.ai_message = self.ai_message + "\n" + "User: " + latest_message + "\n" + "AI_response: " + res
                    self._cr.execute("""select id as client_id, name as client_name, email, commercial_company_name from res_partner""")
                    result = self._cr.fetchall()
                    columns = [desc[0] for desc in self._cr.description]
                    client_df = pd.DataFrame(result, columns=columns)
                    # print("client_df", client_df)
                    res = identify_client(self.ai_message, client_df)
                    self.latest_ai_response = res
                    import json
                    res_df = pd.DataFrame(json.loads(res), index=[0])
                    res_df = res_df.to_html(index=False)
                    latest_channel.with_user(copilot_user).message_post(body=res_df, message_type='comment',
                                                                        subtype_xmlid='mail.mt_comment')
                    latest_channel.with_user(odoo_bot_user).message_post(
                        body="Is the client identified correctly?Answer yes or no. If no give some context",
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment')
                if latest_message.lower() == "yes":
                    self.process_tracker = 'identify_client_done'
                    self.ai_message = self.unstructured_data
                    if self.latest_ai_response is not None:
                        # print("res is not None")
                        import json
                        res_json = json.loads(self.latest_ai_response)
                    else:
                        res_json = {}
                        print("The res variable is None.")
                # print(res_json)
                    self.client_id = str(res_json['client_id'])
                    latest_channel.with_user(odoo_bot_user).message_post(
                        body="Thank you",
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment')
                    latest_channel.with_user(odoo_bot_user).message_post(
                        body="Is the message regarding a quotation or sale order?Answer with quote or so",
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment')

            if self.process_tracker == 'identify_client_done' and messages[0].author_id.name not in ['OdooBot', 'Copilot']:
                impacted_so = ""
                if latest_message.lower() == "quote":
                    self.so_filters = str(('draft', 'sent'))
                    self.process_tracker = 'quote_or_so_identification_started'
                    # print("rfq identified")
                    latest_channel.with_user(odoo_bot_user).message_post(
                        body="Thank you. Please wait while we fetch your quotes",
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment')
                if latest_message.lower() == "so":
                    self.so_filters = "('" + "sale" + "')"
                    self.process_tracker = 'quote_or_so_identification_started'
                    # print("po identified")
                    latest_channel.with_user(odoo_bot_user).message_post(
                        body="Thank you. Please wait while we fetch your sale orders. If AI responds nothing, ask it to fetch again",
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment')

            if self.process_tracker == 'quote_or_so_identification_started':
                if latest_message.lower != "1" and messages[0].author_id.name not in ['OdooBot', 'Copilot']:
                    self._cr.execute("""select
                                            table_3.sale_order,
                                            table_3.state,
                                            table_3.customer_id,
                                            table_3.customer_name,
                                            table_3.client_order_ref,
                                            table_3.product_name,
                                            table_3.product_id,
                                            table_3.qty_ordered,
                                            table_3.qty_delivered,
                                            table_3.price_unit,
                                            table_3.price_total,
                                            table_3.create_date,
                                            table_3.date_order,
                                            table_3.commitment_date,
                                            table_3.lead_time,
                                            table_3.salesperson,
                                            CONCAT(res_partner.street, ' ', COALESCE(res_partner.street2, ''), ' ', res_partner.zip, ' ', res_partner.city) AS shipping_address
                                        from (
                                            select
                                                table_2.sale_order,
                                                table_2.state,
                                                table_2.customer_id,
                                                table_2.partner_shipping_id,
                                                res_partner.commercial_company_name as customer_name,
                                                table_2.client_order_ref,
                                                table_2.product_name,
                                                table_2.product_id,
                                                table_2.qty_ordered,
                                                table_2.qty_delivered,
                                                table_2.price_unit,
                                                table_2.price_total,
                                                table_2.create_date,
                                                table_2.date_order,
                                                table_2.commitment_date,
                                                table_2.lead_time,
                                                table_2.salesperson
                                            from (
                                                select
                                                  table_1.sale_order,
                                                  table_1.state,
                                                  table_1.customer_id,
                                                  table_1.partner_shipping_id,
                                                  table_1.client_order_ref,
                                                  table_1.product_name,
                                                  table_1.product_id,
                                                  table_1.qty_ordered,
                                                  table_1.qty_delivered,
                                                  table_1.price_unit,
                                                  table_1.price_total,
                                                  table_1.create_date,
                                                  table_1.date_order,
                                                  table_1.commitment_date,
                                                  table_1.lead_time,
                                                  hr_employee.name as salesperson
                                                from (
                                                    SELECT
                                                      sale_order.name as sale_order,
                                                      sale_order.state,
                                                      sale_order.partner_id as customer_id,
                                                      sale_order.partner_shipping_id,
                                                      sale_order.client_order_ref,
                                                      sale_order_line.name as product_name,
                                                      sale_order_line.product_id,
                                                      sale_order_line.product_uom_qty AS qty_ordered,
                                                      sale_order_line.qty_delivered,
                                                      sale_order_line.price_unit,
                                                      sale_order_line.price_total,
                                                      sale_order.create_date,
                                                      sale_order.date_order,
                                                      sale_order.commitment_date,
                                                      sale_order_line.customer_lead as lead_time,
                                                      sale_order_line.salesman_id
                                                    FROM sale_order_line
                                                    LEFT JOIN sale_order
                                                      ON sale_order_line.order_id = sale_order.id
                                                    WHERE sale_order.partner_id = {0} and sale_order.state in {1}
                                                    ) as table_1
                                                left join hr_employee on table_1.salesman_id = hr_employee.user_id) as table_2
                                            left join res_partner on table_2.customer_id = res_partner.id) as table_3
                                        left join res_partner on table_3.partner_shipping_id = res_partner.id""".format(self.client_id, self.so_filters))
                    result = self._cr.fetchall()
                    columns = [desc[0] for desc in self._cr.description]
                    so_df = pd.DataFrame(result, columns=columns)
                    so_df_html = so_df.to_html(index=False)
                    res = identify_sale_orders(self.ai_message, so_df)
                    # res = " "
                    self.ai_message = self.ai_message + "\n" + "User: " + latest_message + "\n" + "AI_response: " + impacted_so
                    # remove line breaks from res
                    res = res.replace("\n", "")
                    # check if res is empty
                    if res != "None":
                        self.latest_ai_response = res
                        import json
                        res_json = json.loads(res)
                        res_df = pd.json_normalize(res_json["sale_orders"])
                        # self.identified_so = res_df
                        # check if res_df is not empty
                        # if not res_df.empty:
                        # select all columns except product_id, price_total, price_total_updated and save the new df as display_df
                        display_df = res_df.drop(columns=['product_id', 'price_total', 'price_total_updated'])

                        display_df_html = display_df.to_html(index=False)
                        display_df_html = display_df_html.replace('<table>', '<table style="font-size: 1px;">')
                        latest_channel.with_user(copilot_user).message_post(body=display_df_html, message_type='comment',
                                                                            subtype_xmlid='mail.mt_comment')
                        latest_channel.with_user(odoo_bot_user).message_post(
                            body="Do you want to update these values into the Odoo? Reply with 1 if you do",
                            message_type='comment',
                            subtype_xmlid='mail.mt_comment')
                        order_ids = list(set(res_df['sale_order'].tolist()))
                        # convert order_ids to string and store it in self.order_ids
                        # order_ids = ["S00032"]
                        self.order_ids = str(order_ids)
                        self.process_tracker = "sale_orders_identified"


            if self.process_tracker == "sale_orders_identified":
                if latest_message.lower() == "1":
                    res = self.latest_ai_response
                    import json
                    res_json = json.loads(res)
                    res_df = pd.json_normalize(res_json["sale_orders"])
                    print(res_df)
                    # convert res_df from string to pandas dataframe
                    # iterate through all unique sale orders in res_df
                    for sale_order in list(set(res_df['sale_order'].tolist())):
                        sale_order = sale_order.replace("S", "")
                        sale_order = sale_order.replace("0", "")
                        sale_order = int(sale_order)
                        self.save_orignal_sale_order(sale_order)


                    for index, row in res_df.iterrows():
                        order_id = row['sale_order']
                        product_id = int(row['product_id'])
                        updated_qty = row['qty_ordered_updated']
                        updated_price_unit = row['price_unit_updated']
                        updated_delivery_date = row['delivery_date']
                        # check if the date is in '%m/%d/%Y' format
                        if "/" in updated_delivery_date:
                            # fix for this error in updated_delivery_date: time data '10/13/2023' does not match format '%Y-%m-%d'
                            updated_delivery_date = datetime.strptime(updated_delivery_date, '%m/%d/%Y').strftime(
                                '%Y-%m-%d')

                        order_id = order_id.replace("S", "")
                        order_id = order_id.replace("0", "")
                        order_id = int(order_id)
                        product_id = int(product_id)
                        self.save_orignal_sale_order_line(order_id, product_id)


                        self.update_sale_order_line(order_id, product_id, "product_uom_qty", updated_qty)
                        self.update_sale_order_line(order_id, product_id, "price_unit", updated_price_unit)
                        self.update_sale_order(order_id, "commitment_date", updated_delivery_date)
                        # self.update_sale_order_line(order_id, "price_total", updated_price_total)
                    latest_channel.with_user(odoo_bot_user).message_post(
                        body="All the data is successfully updated in the Odoo. Please type \"revert\" if you want to revert the changes",
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment')
                    latest_channel.with_user(odoo_bot_user).message_post(
                        body="Do you want to track all these sale orders? Reply with yes if you do",
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment')
                    self.process_tracker = "sale_orders_tracking"

            if self.process_tracker == "sale_orders_tracking":
                if latest_message.lower() == "revert":
                    print("sale order lines:", self.sale_order_line_revert)
                    # original_sale_order = self.original_sale_order
                    # original_sale_order_line = self.original_sale_order_line
                    original_sale_order = self.sale_order_revert
                    original_sale_order_line = self.sale_order_line_revert
                    pattern_id = r"'id': (\d+)"
                    match_id = re.search(pattern_id, original_sale_order)
                    if match_id:
                        order_id = int(match_id.group(1))
                        print(order_id)
                    else:
                        print("id not found in the string")
                    pattern_commitment_date = r"'commitment_date': datetime\.datetime\((\d+), (\d+), (\d+), (\d+), (\d+)\)"
                    match_commitment_date = re.search(pattern_commitment_date, original_sale_order)
                    if match_commitment_date:
                        year, month, day, hour, minute = map(int, match_commitment_date.groups())
                        commitment_date = datetime(year, month, day, hour, minute)
                        print("commitment_date", commitment_date)
                        self.update_sale_order(order_id, "commitment_date", commitment_date)
                    else:
                        print("commitment_date not found in the string")


                    # ORDER_LINES
                    pattern_order_id = r"'order_id': \((\d+), '.*'\)"
                    match = re.search(pattern_order_id, original_sale_order_line)
                    # If a match is found, extract the order_id
                    if match:
                        order_id = int(match.group(1))
                        print(order_id)
                    else:
                        print("order_id not found in the string")

                    pattern_product_id = r"'product_id': \((\d+), '.*'\)"
                    match = re.search(pattern_product_id, original_sale_order_line)
                    # If a match is found, extract the product_id
                    if match:
                        product_id = int(match.group(1))
                        print(product_id)
                    else:
                        print("product_id not found in the string")

                    pattern_product_uom_qty = r"'product_uom_qty': (\d+)"
                    match = re.search(pattern_product_uom_qty, original_sale_order_line)
                    # If a match is found, extract the product_uom_qty
                    if match:
                        product_uom_qty = int(match.group(1))
                        print(product_uom_qty)
                    else:
                        print("product_uom_qty not found in the string")

                    pattern_price_unit = r"'price_unit': (\d+)"
                    match = re.search(pattern_price_unit, original_sale_order_line)
                    # If a match is found, extract the price_unit
                    if match:
                        price_unit = int(match.group(1))
                        print(price_unit)
                    else:
                        print("price_unit not found in the string")

                    self.update_sale_order_line(order_id, product_id, "product_uom_qty", product_uom_qty)
                    self.update_sale_order_line(order_id, product_id, "price_unit", price_unit)




                    # for index, row in original_sale_order.iterrows():
                    #     order_id = row['id']
                    #     original_commitment_date = row['commitment_date']
                    #     # fix for this error in original_commitment_date: time data '10/13/2023' does not match format '%Y-%m-%d'
                    #     # original_commitment_date = datetime.strptime(original_commitment_date, '%m/%d/%Y').strftime(
                    #     #     '%Y-%m-%d')
                    #     print("original_commitment_date: ", original_commitment_date)
                    #     self.update_sale_order(order_id, "commitment_date", original_commitment_date)

                    # for index, row in original_sale_order_line.iterrows():
                    #     order_id = row['order_id']
                    #     product_id = row['product_id']
                    #     original_qty = row['product_uom_qty']
                    #     original_price_unit = row['price_unit']
                    #     self.update_sale_order_line(order_id, product_id, "product_uom_qty", original_qty)
                    #     self.update_sale_order_line(order_id, product_id, "price_unit", original_price_unit)




            if self.process_tracker == "sale_orders_tracking":
                if latest_message.lower() == "yes":
                    self.process_tracker = "sale_orders_tracking"
                    order_ids = self.order_ids
                #     convert order_ids to list
                    order_ids = order_ids.replace("[", "")
                    order_ids = order_ids.replace("]", "")
                    order_ids = order_ids.replace("'", "")
                    order_ids = order_ids.split(",")
                    print("order_ids: ", order_ids)
                    for order_id in order_ids:
                        order_id = order_id.replace(" ", "")
                        sale_order_tracking = track_sale_orders(self._cr, order_id)
                        latest_channel.with_user(copilot_user).message_post(body=sale_order_tracking,
                                                                            message_type='comment',
                                                                            subtype_xmlid='mail.mt_comment')


        return rdata