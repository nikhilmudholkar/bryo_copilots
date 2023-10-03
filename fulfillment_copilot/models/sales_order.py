from odoo import api, fields, models
import requests
import json
# import sale.order
# import ir.ui.view


class SaleOrder(models.Model):
    _name = "bryo.copilot"
    _description = "Bryo fulfillment copilot"
    # _inherit = "res.partner"
    # print("********************************")

    # GetSaleOrderId()
    # description_sale = fields.Text('Sales Description')
    order_name = fields.Char(string='Order Reference', required=True)
    order_date = fields.Date(string='Order Date', required=True)
    order_status = fields.Boolean(string='Is Pending', default=True)

    # def getdata(self):
    #     print("inside getdata")
    #     print(self.env['sale.order'].search([]))
    #     print(self.env['sale.order'].search([]).mapped('name'))
    #     print(self.env['sale.order'].search([]).mapped('date_order'))
    #     print(self.env['sale.order'].search([]).mapped('amount_total'))
    #
    #     url = "https://hooks.slack.com/services/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"
    #     # payload for slack webhook endpoint to send messages to a channel
    #     slack_data = {'text': "This is a sample message from odoo"}
    #
    #     response = requests.post(
    #         url, data=json.dumps(slack_data),
    #         headers={'Content-Type': 'application/json'}
    #     )
    #     print(response.text)
    #
    #     notification = {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'title': "Bryo Copilot!",
    #             'message': "THis is a sample test message for bryo copilot",
    #         },
    #     }
    #     message = {
    #         'title': "Bryo Copilot!",
    #         'message': "THis is a sample test message for bryo copilot",
    #     }
    #     print(self.env.user.id)
    #     self.env['bus.bus']._sendone(self.env.user.id, 'ir.actions.client', message)


    def getdata(self):
        url = "http://35.92.128.67:8000/askai"
            # payload for slack webhook endpoint to send messages to a channel
        # payload = {
        #     "question": "Q: Who is elon musk? A: ",
        #     "max_tokens": 100,
        #     "stop": ["Q:", "\n"],
        #     "security_token": "bryo_access_control_1",
        #     # "echo": "true"
        # }
        payload = {
            "security_token": "bryo_access_control_1",
            "context": "answer everything in haiku",
            "message": "how many plants are there in solar system?"

        }

        response_llama = requests.post(
            url, data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        response_llama = response_llama.json()
        # print(response_llama["choices"][0]["text"])

        url_slack = "https://hooks.slack.com/services/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"
            # payload for slack webhook endpoint to send messages to a channel
        slack_data = {'text': str(response_llama["choices"][0]["text"])}

        # print(slack_data)
        # print(response_llama.text)
        # print(type(slack_data))
        # print(str(response_llama.text))
        response = requests.post(
            url_slack, data=json.dumps(slack_data),
            headers={'Content-Type': 'application/json'}
        )
        # print(response.text)
    #
    # @api.model
    # def init(self):

    # @api.model
    # def init(self):
    #     url = "http://35.92.128.67:8000/askai"
    #     # payload for slack webhook endpoint to send messages to a channel
    #     payload = {
    #         "question": "Q: Who is elon musk? A: ",
    #         "max_tokens": 100,
    #         "stop": ["Q:", "\n"],
    #         "security_token": "dndksnjcsnjkcnzjxncjknc",
    #         # "echo": "true"
    #     }
    #
    #     response_llama = requests.post(
    #         url, data=json.dumps(payload),
    #         headers={'Content-Type': 'application/json'}
    #     )
    #     response_llama = response_llama.json()
    #     print(response_llama.json())
    #     print(response_llama["choices"][0]["text"])
    #
    #     url_slack = "https://hooks.slack.com/services/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"
    #     # payload for slack webhook endpoint to send messages to a channel
    #     slack_data = {'text': str(response_llama["choices"][0]["text"])}
    #
    #     print(slack_data)
    #     # print(response_llama.text)
    #     print(type(slack_data))
    #     # print(str(response_llama.text))
    #     response = requests.post(
    #         url_slack, data=json.dumps(slack_data),
    #         headers={'Content-Type': 'application/json'}
    #     )
    #     print(response.text)






    # partner_id = fields.Many2one('res.partner', string='Customer', required=True, change_default=True, index=True, track_visibility='always')

