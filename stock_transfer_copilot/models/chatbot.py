import datetime
import json
import requests
from odoo import api, fields, models, tools
import pandas as pd
# from utils import create_llm_prompt

class chatbotview(models.Model):
    _name = "stock.transfer.chatbot"
    _auto = False
    _description = "stock transfer chatbot"
    name = fields.Char(string='Stock Transfer Copilot', required=True)

    # @api.model
    # def init(self):
    #     message = "stock transfer copliot suggestions"
    #     print(message)
    #     if self.env['mail.channel'].search([('name', '=', "Bryo stock transfer copilot suggestions")]).id:
    #         channel_id = self.env['mail.channel'].search([('name', '=', "stock transfer copilot suggestions")]).id
    #         # print(channel_id)
    #         self.env['mail.channel'].browse(channel_id).message_post(body=message, message_type='comment')
