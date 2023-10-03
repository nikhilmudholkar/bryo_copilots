import base64
# import json

import pandas as pd

import odoo
from odoo import api, fields, models, _
from .create_llm_prompt import askai, remove_tags, askaileadtimeimpact, askaidelayedproducts, \
    askaidelayedmanufacturingproducts, uploadpdftollm, create_message_draft
from .query_computations import calculate_impacted_saleorders, calculate_impacted_manufacturing_orders
from odoo.exceptions import UserError


class Channel(models.Model):
    # added test comment
    _inherit = 'mail.channel'
    process_tracker = fields.Char(string="Process Tracker", default="process_started")
    unstructured_data = fields.Char(string="Unstructured Data", default="unstructured_data")
    unstructured_data_formatted = fields.Char(string="Unstructured Data Formatted", default="unstructured_data_formatted")
    latest_ai_response = fields.Char(string="Latest AI Response", default="latest_ai_response")
    vendor_id = fields.Char(string="Vendor ID", default="vendor_id")
    # create a new field product ids which is a list
    product_ids = fields.Char(string="Product IDs", default="product_ids")
    ai_message = fields.Char(string="AI Message", default="")
    purchase_orders = fields.Char(string="Purchase Orders", default="")
    rfq = fields.Boolean(string="RFQ", default=False)
    impacted_so = fields.Char(string="Impacted SO", default="")
    impacted_mo = fields.Char(string="Impacted MO", default="")

    # @api.model
    # def init(self):
    #     super().init()
    #
    #     # Save the variable into self
    #     self.process_tracker = 'process_started'

    # The if conditions are there to stop the recursion! Research about why they are there and how can we remove them
    def _notify_thread(self, message, msg_vals=False, json=None, **kwargs):
        # print(self.process_tracker)
        # print(self.unstructured_data)
        if self.process_tracker == 'process_completed':
            self.process_tracker = 'process_started'
        rdata = super(Channel, self)._notify_thread(message, msg_vals=msg_vals, **kwargs)
        bard_suggestions_channel = self.env.ref('lead_time_copilot.channel_bard_suggestions')
        bryo_channels = self.env['mail.channel'].search([('name', 'ilike', '%Bryo%')])
        bryo_channel_ids = [channel.id for channel in bryo_channels]

        copilot_user = self.env.ref("lead_time_copilot.copilot_user")
        # print id of copilot user
        print("copilot_user_id: ", copilot_user.id)
        print("OdooBot user id: ", self.env["res.partner"].search([('display_name', '=', 'OdooBot')]))
        # print(self.env['odoo.bot.user'].sudo().search([('name', '=', 'OdooBot')])[0])
        odoo_bot_user = self.env.ref("base.user_root")
        # odoo_bot_author_id =
        print("odoo_bot_user: ", odoo_bot_user.id)
        partner_copilot = self.env.ref("lead_time_copilot.copilot_user_partner")
        author_id = msg_vals.get('author_id')
        copilot_name = str(partner_copilot.name or '') + ', '
        res = "*****THIS IS A TEST BARD SUGGESTION*****"
        Partner = self.env['res.partner']
        if author_id:
            partner_id = Partner.browse(author_id)
            if partner_id:
                partner_name = partner_id.name

        if author_id != partner_copilot.id and copilot_name in msg_vals.get('record_name',
                                                                            '') or 'ChatGPT,' in msg_vals.get(
            'record_name', '') and self.channel_type == 'chat':
            try:
                res = "Here is the history of all the messages in this channel:"
                messages = self.message_ids
                history = ''
                for message in messages:
                    temp_author_id = message.author_id.id
                    author_name = self.env['res.partner'].search([('id', '=', temp_author_id)]).name
                    history += f'{author_name}: {message.body}'
                    history += '\n'

                res += '\n\n**Message History**\n' + history
                latest_message = remove_tags(messages[0].body)
                if latest_message == "askai":
                    res = askai(res)
                if latest_message == "create channel for transfer":
                    new_channel = self.env['mail.channel'].create({
                        'name': 'Transfer channel 1',
                        'public': False,
                    })
                    res = f'Created new channel {new_channel.name}'

                self.with_user(copilot_user).message_post(body=res, message_type='comment',
                                                          subtype_xmlid='mail.mt_comment')
            except Exception as e:
                raise UserError(_(e))
        # rewrite the follwing if condition such that it checks if msg_vals('record_name') is in the list of channel names
        elif author_id != partner_copilot.id and msg_vals.get('model', '') == 'mail.channel' and msg_vals.get('res_id',
                                                                                                              0) in bryo_channel_ids:
            try:
                messages = self.message_ids
                print("latest message from", messages[0].author_id.name)


                latest_message = remove_tags(messages[0].body)
                latest_author_id = messages[0].author_id.id
                latest_channel_name = messages[0].record_name
                latest_channel = self.env['mail.channel'].search([('name', '=', latest_channel_name)])
                latest_message_attachment = messages[0].attachment_ids
                # print("attachment", attachment)
                if latest_message_attachment:
                    attachment = latest_channel.message_ids.mapped('attachment_ids')[0]
                    # print("Attachment is present")
                    pdf_file = base64.decodebytes(attachment.datas)
                    with open(
                            '/Users/nikhilmukholdar/Personal/fintel_labs/odoo_global/odoo/dev/lead_time_copilot/my_pdf_file.pdf',
                            'wb') as f:
                        f.write(pdf_file)
                    response = uploadpdftollm(
                        '/Users/nikhilmukholdar/Personal/fintel_labs/odoo_global/odoo/dev/lead_time_copilot/my_pdf_file.pdf')
                    # latest_channel.with_user(copilot_user).message_post(body=response, message_type='comment',
                    #                                                     subtype_xmlid='mail.mt_comment')
                    response = response.replace('\n', ' ')
                    self.unstructured_data = response
                    self.process_tracker = 'identify_vendor'
                    latest_message = response


                # store the first email is self
                if self.process_tracker == 'process_started':
                    self.process_tracker = 'identify_vendor'
                    self.unstructured_data = latest_message
                    self.unstructured_data_formatted = messages[0].body
                    # replace <br> with \n
                    self.unstructured_data_formatted = self.unstructured_data_formatted.replace("<br>", "\n")
                    self.unstructured_data_formatted = self.unstructured_data_formatted.replace("<p>", "")
                    self.unstructured_data_formatted = self.unstructured_data_formatted.replace("</p>", "")
                    print("LATEST MESSAGE: ", self.unstructured_data_formatted)
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
                    print("process completed")
                # check if latest message contains askai
                if self.process_tracker == 'identify_vendor':
                    # print("INSIDE IDENTIFY VENDOR")
                    # messages[0].author_id.id not in [partner_copilot.id, odoo_bot_user.id]:
                    # self.process_tracker = 'identify_vendor'
                    # TODO    loop is correct. Ideally it should be in loop until user says yes, we just need to take input from user to type tht!
                    if latest_message.lower() != "yes" and messages[0].author_id.name not in ['OdooBot', 'Copilot']:
                    # print("author_id: ", messages[0].author_id.id)
                    # if latest_message.lower() != "yes" and messages[0].author_id.id not in [copilot_user.id, odoo_bot_user.id]:
                    #     print("asking AI")
                        self.ai_message = self.ai_message + "\n" + "User: " + latest_message + "\n" + "AI_response: " + res
                        self._cr.execute("""select id,
                                            commercial_company_name 
                                            from res_partner
                                            where is_company  = true
                                            and id in (select partner_id from purchase_order)""")
                        result = self._cr.fetchall()
                        columns = [desc[0] for desc in self._cr.description]
                        vendor_df = pd.DataFrame(result, columns=columns)
                        # print(vendor_df)
                        res = askai(self.ai_message, vendor_df)
                        # print(res)
                        self.latest_ai_response = res
                        # convert res json into a pandasdataframe and then convert this dataframe into html
                        import json
                        res_df = pd.DataFrame(json.loads(res), index=[0])
                        res_df = res_df.to_html(index=False)
                        latest_channel.with_user(copilot_user).message_post(body=res_df, message_type='comment',
                                                                            subtype_xmlid='mail.mt_comment')
                        latest_channel.with_user(odoo_bot_user).message_post(
                            body="Is the vendor identified correctly?Answer yes or no. If no give some context",
                            message_type='comment',
                            subtype_xmlid='mail.mt_comment')
                    if latest_message.lower() == "yes":
                        self.process_tracker = 'identify_vendor_done'
                        self.ai_message = self.unstructured_data
                        # print("vendor identified successfully")
                        # print(self.process_tracker)
                        # print("loading into json")
                        if self.latest_ai_response is not None:
                            # print("res is not None")
                            import json
                            print(self.latest_ai_response)
                            res_json = json.loads(self.latest_ai_response)
                        else:
                            res_json = {}
                            print("The res variable is None.")
                        # print(res_json)
                        self.vendor_id = str(res_json['vendor_id'])
                        latest_channel.with_user(odoo_bot_user).message_post(
                            body="Thank you",
                            message_type='comment',
                            subtype_xmlid='mail.mt_comment')
                        latest_channel.with_user(odoo_bot_user).message_post(
                            body="Is the message regarding a rfq or purchase order?Answer with rfq or po",
                            message_type='comment',
                            subtype_xmlid='mail.mt_comment')

                        # return rdata

                # ask user if the message is about rfq or purchase order?
                if self.process_tracker == 'identify_vendor_done' and messages[0].author_id.name not in ['OdooBot', 'Copilot']:
                    # latest_channel.with_user(odoo_bot_user).message_post(
                    #     body="Is the message regarding rfq or purchase order?Answer rfq or po",
                    #     message_type='comment',
                    #     subtype_xmlid='mail.mt_comment')
                    if latest_message.lower() == "rfq":
                        self.rfq = True
                        self.process_tracker = 'PO_or_RFQ_identification_started'
                        # print("rfq identified")
                        latest_channel.with_user(odoo_bot_user).message_post(
                            body="Thank you. Please wait while we fetch your RFQs",
                            message_type='comment',
                            subtype_xmlid='mail.mt_comment')
                    if latest_message.lower() == "po":
                        self.rfq = False
                        self.process_tracker = 'PO_or_RFQ_identification_started'
                        # print("po identified")
                        latest_channel.with_user(odoo_bot_user).message_post(
                            body="Thank you. Please wait while we fetch your POs",
                            message_type='comment',
                            subtype_xmlid='mail.mt_comment')

                if self.rfq is True and self.process_tracker == 'PO_or_RFQ_identification_started':
                    # purchase orders tabel
                    po_or_rfq = ""
                    ai_message = ""
                    if latest_message.lower() != "1" and messages[0].author_id.name not in ['OdooBot', 'Copilot']:
                        print("inside rfq")
                        # self.ai_message = self.ai_message + "/n" + latest_message
                        self.ai_message = self.ai_message + "\n" + "User: " + latest_message + "\n" + "AI_response: " + po_or_rfq
                        self._cr.execute("""SELECT
                                              table_1.partner_id as vendor_id,
                                              table_1.commercial_company_name as vendor_name,
                                              table_1.name AS po_name,
                                              purchase_order_line.product_id,
                                              purchase_order_line.name AS product_name,
                                              purchase_order_line.product_qty AS ordered_qty,
                                              purchase_order_line.date_planned
                                            FROM purchase_order_line
                                            LEFT JOIN (
                                              SELECT
                                                purchase_order.id AS PO_ID,
                                                purchase_order.partner_id,
                                                purchase_order.receipt_status,
                                                purchase_order.name,
                                                purchase_order.state,
                                                purchase_order.partner_ref,
                                                res_partner.commercial_company_name
                                              FROM purchase_order
                                              INNER JOIN res_partner
                                                ON purchase_order.partner_id = res_partner.id
                                            ) AS table_1
                                            ON purchase_order_line.order_id = table_1.PO_ID
                                            WHERE table_1.state = 'sent'
                                            AND table_1.partner_id = {0};""".format(str(self.vendor_id)))
                        result = self._cr.fetchall()
                        columns = [desc[0] for desc in self._cr.description]
                        rfq_df = pd.DataFrame(result, columns=columns)
                        po_or_rfq = askaileadtimeimpact(self.ai_message, rfq_df, True)
                        self.latest_ai_response = po_or_rfq
                        # print(po_or_rfq)
                        json_list = eval(po_or_rfq)

                        # Create a Pandas DataFrame from the list of Python dictionaries
                        po_df = pd.DataFrame(json_list)
                        po_df = po_df.to_html(index=False)
                        latest_channel.with_user(copilot_user).message_post(body="Here is the purchase order with the "
                                                                                 "new quantities and delivery dates",
                                                                            message_type='comment',
                                                                            subtype_xmlid='mail.mt_comment')
                        latest_channel.with_user(copilot_user).message_post(body=po_df, message_type='comment',
                                                                            subtype_xmlid='mail.mt_comment')
                        latest_channel.with_user(odoo_bot_user).message_post(
                            body="Is the Purchase Order identified correctly?\nIf yes, type '1'.\nIf no, give some context",
                            message_type='comment',
                            subtype_xmlid='mail.mt_comment')

                    if latest_message.lower() == "1":
                        # change this to include multiple products

                        self.process_tracker = 'po_rfq_done'
                        self.ai_message = ""
                        print(self.process_tracker)
                        json_list = []
                        if self.latest_ai_response is not None:
                            print("res is not None")
                            import json
                            print(self.latest_ai_response)
                            self.latest_ai_response = self.latest_ai_response.replace('```', '')
                            self.latest_ai_response = self.latest_ai_response.replace('\n', '')
                            json_str = self.latest_ai_response
                            # if json_str is not enclosed by [], add [] to it
                            if not json_str.startswith('['):
                                json_str = '[' + json_str
                            if not json_str.endswith(']'):
                                json_str = json_str + ']'
                            json_list = json.loads(json_str)
                        else:
                            po_or_rfq_json = {}
                            print("The res variable is None.")
                        print(json_list)
                        self.purchase_orders = str(json_list)
                        # extract all the product_id from json_list and store it in self.product_ids
                        product_ids = []
                        if isinstance(json_list, list):
                            for json_dict in json_list:
                                product_ids.append(json_dict['product_id'])
                            self.product_ids = str(product_ids)
                            print(self.product_ids)
                        else:
                            product_ids.append(json_list['product_id'])
                            self.product_ids = str(product_ids)
                            print(self.product_ids)

                if self.rfq is False and self.process_tracker == 'PO_or_RFQ_identification_started':
                    print("outside rfq")
                    po_or_rfq = ""

                    if latest_message.lower() != "1" and messages[0].author_id.name not in ['OdooBot', 'Copilot']:
                        # print("ai message for identifying po " + self.ai_message)
                        self.ai_message = self.ai_message + "\n" + "User: " + latest_message + "\n" + "AI_response: " + po_or_rfq
                        self._cr.execute("""SELECT
                                              table_1.partner_id as vendor_id,
                                              table_1.commercial_company_name as vendor_name,
                                              table_1.name AS po_name,
                                              purchase_order_line.product_id,
                                              purchase_order_line.name AS product_name,
                                              purchase_order_line.product_qty AS ordered_qty,
                                              purchase_order_line.date_planned
                                            FROM purchase_order_line
                                            LEFT JOIN (
                                              SELECT
                                                purchase_order.id AS PO_ID,
                                                purchase_order.partner_id,
                                                purchase_order.receipt_status,
                                                purchase_order.name,
                                                purchase_order.state,
                                                purchase_order.partner_ref,
                                                res_partner.commercial_company_name
                                              FROM purchase_order
                                              INNER JOIN res_partner
                                                ON purchase_order.partner_id = res_partner.id
                                            ) AS table_1
                                            ON purchase_order_line.order_id = table_1.PO_ID
                                            WHERE table_1.receipt_status = 'pending'
                                            AND table_1.state = 'purchase'
                                            AND table_1.partner_id = {0};""".format(str(self.vendor_id)))
                        result = self._cr.fetchall()
                        columns = [desc[0] for desc in self._cr.description]
                        po_df = pd.DataFrame(result, columns=columns)

                        po_or_rfq = askaileadtimeimpact(self.ai_message, po_df, False)
                        # print("********")
                        # print(po_or_rfq)
                        # print("********")
                        # extract a list from po_or_rfq. The list starts with [ and ends with ]
                        start_index = po_or_rfq.find("[")
                        end_index = po_or_rfq.rfind("]")
                        json_string = po_or_rfq[start_index:end_index + 1]
                        # print(json_string)
                        # print
                        import json
                        json_list_str = json.loads(json_string)
                        str_message = po_or_rfq[0:start_index]
                        # print(json_list_str)

                        self.latest_ai_response = json_string
                        json_list = eval(json_string)

                        # Create a Pandas DataFrame from the list of Python dictionaries
                        po_df = pd.DataFrame(json_list)
                        po_df = po_df.to_html(index=False)
                        latest_channel.with_user(copilot_user).message_post(body="Here is the purchase order with the "
                                                                                 "new quantities and delivery dates",
                                                                            message_type='comment',
                                                                            subtype_xmlid='mail.mt_comment')
                        latest_channel.with_user(copilot_user).message_post(body=po_df, message_type='comment',
                                                                            subtype_xmlid='mail.mt_comment')
                        latest_channel.with_user(copilot_user).message_post(body=str_message, message_type='comment',
                                                                            subtype_xmlid='mail.mt_comment')
                        latest_channel.with_user(odoo_bot_user).message_post(
                            body="Is the Purchase Order identified correctly?\nIf yes, type '1'.\nIf no, give some context",
                            message_type='comment',
                            subtype_xmlid='mail.mt_comment')
                        # self.ai_message = self.ai_message + "\n" + "User: " + latest_message + "\n" + "AI_response: " + po_or_rfq
                    if latest_message.lower() == "1":
                        # change this to include multiple products
                        self.process_tracker = 'po_rfq_done'
                        self.ai_message = ""
                        # print(self.process_tracker)
                        json_list = []
                        if self.latest_ai_response is not None:
                            # print("res is not None")
                            import json
                            # print(self.latest_ai_response)
                            # remove ``` from the response
                            self.latest_ai_response = self.latest_ai_response.replace('```', '')
                            self.latest_ai_response = self.latest_ai_response.replace('\n', '')
                            # self.latest_ai_response = self.latest_ai_response.replace(',', '')
                            # print(self.latest_ai_response)
                            #
                            json_str = self.latest_ai_response
                            # print(json_str)
                            if not json_str.startswith('['):
                                json_str = '[' + json_str
                            if not json_str.endswith(']'):
                                json_str = json_str + ']'
                            # if json_str.startswith('{'):
                            #     json_list.append(json.loads(json_str))
                            # else:
                            #     for json_str in json_str.split(','):
                            #         if json_str.endswith('}'):
                            #             json_str = json_str[1:]
                            #             json_list.append(json.loads(json_str))
                            json_list = json.loads(json_str)
                        else:
                            po_or_rfq_json = {}
                            print("The res variable is None.")
                        # print(json_list)
                        self.purchase_orders = str(json_list)
                        # extract all the product_id from json_list and store it in self.product_ids
                        product_ids = []
                        # check if the json_list is a list of dictionaries or a dictionary
                        if isinstance(json_list, list):
                            for json_dict in json_list:
                                product_ids.append(json_dict['product_id'])
                            self.product_ids = str(product_ids)
                            # print(self.product_ids)
                        else:
                            product_ids.append(json_list['product_id'])
                            self.product_ids = str(product_ids)
                            # print(self.product_ids)
                        # for json_dict in json_list:
                        #     product_ids.append(json_dict['product_id'])
                        # self.product_ids = str(product_ids)
                        # print(self.product_ids)
                # replace [ and ] with ( and ) for the query in product_ids
                if self.process_tracker == 'po_rfq_done' and messages[0].author_id.name not in ['OdooBot', 'Copilot']:
                    latest_channel.with_user(odoo_bot_user).message_post(
                        body="Thank you! Please wait while we fetch the impacted sale orders and manufacturing orders",
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment')
                    product_ids = str(self.product_ids).replace('[', '(').replace(']', ')')
                    self._cr.execute("""SELECT
                                          table_2.product_id,
                                          table_3.name AS product_name,
                                          table_2.company_name,
                                          table_2.location,
                                          table_2.quantity,
                                          table_2.reserved_quantity
                                        FROM (
                                          SELECT
                                            stock_quant.product_id,
                                            table_1.name AS company_name,
                                            table_1.complete_name AS location,
                                            stock_quant.quantity,
                                            stock_quant.reserved_quantity
                                          FROM stock_quant
                                          LEFT JOIN (
                                            SELECT
                                              stock_location.id,
                                              res_company.name,
                                              stock_location.complete_name
                                            FROM stock_location
                                            LEFT JOIN res_company
                                              ON stock_location.company_id = res_company.id
                                          ) AS table_1
                                            ON stock_quant.location_id = table_1.id
                                          WHERE stock_quant.inventory_date IS NOT NULL
                                        ) AS table_2
                                        LEFT JOIN (
                                          SELECT
                                            DISTINCT product_id,
                                            name
                                          FROM purchase_order_line
                                          where purchase_order_line.product_id in {0}
                                        ) AS table_3
                                          ON table_2.product_id = table_3.product_id
                                        WHERE table_2.product_id IN (table_3.product_id);""".format(product_ids))
                    print("query executed")
                    result = self._cr.fetchall()
                    columns = [desc[0] for desc in self._cr.description]
                    inventory_df = pd.DataFrame(result, columns=columns)

                    # Orders that could be impacted by delayed products
                    self._cr.execute("""select
                                          table_1.name  as sale_order,
                                          table_1.product_name,
                                          table_1.product_id,
                                          table_1.qty_ordered,
                                          table_1.qty_delivered,
                                          table_1.commitment_date,
                                          table_1.lead_time,
                                          hr_employee.name as salesperson
                                        from (
                                            SELECT
                                              sale_order.name,
                                              sale_order_line.name as product_name,
                                              sale_order_line.product_id,
                                              sale_order_line.product_uom_qty AS qty_ordered,
                                              sale_order_line.qty_delivered,
                                              commitment_date,
                                              sale_order_line.customer_lead as lead_time,
                                              user_id
                                            FROM sale_order_line
                                            LEFT JOIN sale_order
                                              ON sale_order_line.order_id = sale_order.id
                                            WHERE sale_order_line.product_id IN {0}
                                            AND sale_order.delivery_status = 'pending'
                                            ) as table_1
                                        left join hr_employee on table_1.user_id = hr_employee.user_id""".format(
                        product_ids))
                    result = self._cr.fetchall()
                    columns = [desc[0] for desc in self._cr.description]
                    sales_order_df = pd.DataFrame(result, columns=columns)

                    # res = askaidelayedproducts(latest_message, inventory_df, sales_order_df)
                    res = calculate_impacted_saleorders(inventory_df, sales_order_df, self.purchase_orders)
                    # self.impacted_so = res.to_string(index=False)
                    self.impacted_so = res.to_csv(index=False)
                    # self.impacted_so = res.to_json(orient='records')
                    res = res.to_html(index=False)
                    latest_channel.with_user(copilot_user).message_post(body=res, message_type='comment',
                                                                        subtype_xmlid='mail.mt_comment')

                    # Manufacturing orders that could be impacted by delayed products. Commented out because query is throwing error
                    self._cr.execute("""select
                                            table_2.name as manuf_order ,
                                            table_2.bom_product_name,
                                            table_2.bom_product_id,
                                            table_2.bom_product_qty,
                                            table_2.date_planned_start,
                                            table_2.date_deadline,
                                            table_2.manuf_lead_time,
                                            hr_employee.name as responsible
                                        FROM (
                                            SELECT
                                              table_1.name,
                                              CONCAT(product_template.default_code, ' ', product_template.name) AS bom_product_name,
                                              table_1.bom_product_id,
                                              table_1.bom_product_qty,
                                              table_1.date_planned_start,
                                              table_1.date_planned_finished,
                                              table_1.date_deadline,
                                              product_template.produce_delay as manuf_lead_time,
                                              table_1.user_id
                                            FROM (
                                              SELECT
                                                mrp_production.name,
                                                mrp_production.product_id AS MO_product_id,
                                                mrp_bom_line.product_id AS bom_product_id,
                                                mrp_bom_line.product_qty*mrp_production.product_qty AS bom_product_qty,
                                                mrp_production.date_planned_start,
                                                mrp_production.date_planned_finished,
                                                mrp_bom_line.product_tmpl_id,
                                                mrp_production.date_deadline,
                                                mrp_production.user_id
                                              FROM mrp_bom_line
                                              LEFT JOIN mrp_production ON mrp_bom_line.bom_id = mrp_production.bom_id
                                              where mrp_bom_line.product_id in {0}
                                              and mrp_production.state = 'confirmed'
                                            ) AS table_1
                                            LEFT JOIN product_template ON table_1.product_tmpl_id = product_template.id
                                            ) as table_2
                                        LEFT JOIN hr_employee ON table_2.user_id = hr_employee.user_id""".format(
                        product_ids))
                    result = self._cr.fetchall()
                    columns = [desc[0] for desc in self._cr.description]
                    manufacturing_orders_df = pd.DataFrame(result, columns=columns)
                    print(manufacturing_orders_df)

                    # bard_suggestions_channel.with_user(copilot_user).message_post(body=res, message_type='comment',
                    #                                                               subtype_xmlid='mail.mt_comment')
                    # res = askaidelayedmanufacturingproducts(latest_message, inventory_df, manufacturing_order_df)
                    res = calculate_impacted_manufacturing_orders(inventory_df, manufacturing_orders_df,
                                                                  self.purchase_orders)
                    # self.impacted_mo = res.to_string(index=False)
                    self.impacted_mo = res.to_csv(index=False)
                    # self.impacted_mo = res.to_json(orient='records')
                    # print("---------------")
                    # print(self.impacted_mo)
                    # print("---------------")
                    res = res.to_html(index=False)
                    latest_channel.with_user(copilot_user).message_post(body=res, message_type='comment',
                                                                        subtype_xmlid='mail.mt_comment')


                    self.process_tracker = "creating_draft"

                    latest_channel.with_user(copilot_user).message_post(body="Do you want to notify the responsible person via slack or email? Reply with slack/email", message_type='comment',
                                                                        subtype_xmlid='mail.mt_comment')
                if self.process_tracker == "creating_draft" and latest_message == "slack":
                    draft_msg = create_message_draft("slack", self.unstructured_data_formatted, self.impacted_so, self.impacted_mo)
                    latest_channel.with_user(copilot_user).message_post(
                        body=draft_msg,
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment')

                if self.process_tracker == "creating_draft" and latest_message == "email":
                    draft_msg = create_message_draft("email", self.unstructured_data_formatted, self.impacted_so, self.impacted_mo)
                    latest_channel.with_user(copilot_user).message_post(
                        body=draft_msg,
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment')



                # if self.process_tracker == "creating_draft" and latest_message == "email":
                #     latest_channel.with_user(copilot_user).message_post(
                #         body="Creating a message for slack",
                #         message_type='comment',
                #         subtype_xmlid='mail.mt_comment')

                    latest_channel.with_user(odoo_bot_user).message_post(body="exit", message_type='comment',
                                                                         subtype_xmlid='mail.mt_comment')

            except Exception as e:
                raise UserError(_(e))
        return rdata
