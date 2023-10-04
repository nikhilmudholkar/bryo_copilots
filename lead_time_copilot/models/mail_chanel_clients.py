import base64
import pandas as pd
import odoo
from odoo import api, fields, models, _


class Channel_clients(models.Model):
    _inherit = 'mail.channel'

    def _notify_thread(self, message, msg_vals=False, json=None, **kwargs):
        print("inside notify message loop for clients")
        print("message", message)
