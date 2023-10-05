import base64
import pandas as pd
import odoo
from odoo import api, fields, models, _
from .create_llm_prompt import askai, remove_tags, uploadpdftollm


class Channel_clients(models.Model):
    _inherit = 'mail.channel'
    unstructured_data_clients = fields.Char(string="Unstructured Data Clients", default="unstructured_data_clients")

    def notify_thread(self, message, msg_vals=False, json=None, **kwargs):
        print("inside notify message loop for clients")
        print("message", message)

        copilot_user = self.env.ref("lead_time_copilot.copilot_user")
        odoo_bot_user = self.env.ref("base.user_root")
        messages = self.message_ids
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
                    '/Users/nikhilmukholdar/Personal/fintel_labs/odoo_global/odoo/dev/lead_time_copilot/my_pdf_file_clients.pdf',
                    'wb') as f:
                f.write(pdf_file)
            response = uploadpdftollm(
                '/Users/nikhilmukholdar/Personal/fintel_labs/odoo_global/odoo/dev/lead_time_copilot/my_pdf_file_clients.pdf')
            # latest_channel.with_user(copilot_user).message_post(body=response, message_type='comment',
            #                                                     subtype_xmlid='mail.mt_comment')
            # response = response.replace('\n', ' ')
            # self.unstructured_data = response
            # self.process_tracker = 'identify_vendor'
            latest_message = response
            print(latest_message)
            # convert response to html
            response = response.replace('\n', '<br/>')
            response = '<p>' + response + '</p>'
            latest_channel.with_user(copilot_user).message_post(body=response, message_type='comment',
                                                                subtype_xmlid='mail.mt_comment')

            self.unstructured_data_clients = response
            print("response from mail_channel_clients.py", self.unstructured_data_clients)





