from odoo import api, fields, models, _
from .create_llm_prompt import askai, remove_tags
from odoo.exceptions import UserError


class Channel(models.Model):
    _inherit = 'mail.channel'

    # The if conditions are there to stop the recursion! Research about why they are there and how can we remove them
    def _notify_thread(self, message, msg_vals=False, **kwargs):
        rdata = super(Channel, self)._notify_thread(message, msg_vals=msg_vals, **kwargs)
        bard_suggestions_channel = self.env.ref('stock_transfer_copilot.channel_bard_suggestions')
        bryo_channels = self.env['mail.channel'].search([('name', 'ilike', '%Bryo%')])
        bryo_channel_ids = [channel.id for channel in bryo_channels]
        # bryo

        copilot_user = self.env.ref("stock_transfer_copilot.copilot_user")
        partner_copilot = self.env.ref("stock_transfer_copilot.copilot_user_partner")
        author_id = msg_vals.get('author_id')
        copilot_name = str(partner_copilot.name or '') + ', '
        prompt = msg_vals.get('body')
        if not prompt:
            return rdata
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
        # elif author_id != partner_copilot.id and msg_vals.get('model', '') == 'mail.channel':
            try:
                res = "*****THIS IS A TEST BARD SUGGESTION*****"
                # res = "Here is the history of all the messages in this channel:"
                messages = self.message_ids
                history = ''
                for message in messages:
                    temp_author_id = message.author_id.id
                    author_name = self.env['res.partner'].search([('id', '=', temp_author_id)]).name
                    history += f'{author_name}: {message.body}'
                    history += '\n'
                # res += '\n\n**Message History**\n' + history
                latest_message = remove_tags(messages[0].body)
                latest_channel_name = messages[0].record_name

                latest_channel = self.env['mail.channel'].search([('name', '=', latest_channel_name)])
                # get the channel where the latest_message was sent

                if latest_message == "askai":
                    res = askai(res)

                if latest_message == "create channel for transfer":
                    new_channel = self.env['mail.channel'].create({
                        'name': 'Bryo Transfer channel 1'
                    })
                    res = f'Created new channel {new_channel.name}'

                # achive new_channel if msg is archive channel for transfer
                if latest_message == "archive channel for transfer":
                    archive_channel = self.env['mail.channel'].search([('name', '=', 'Transfer channel 1')])
                    archive_channel.write({'active': False})
                    res = f'Archive channel {archive_channel.name}'

                if latest_channel.id in bryo_channel_ids:
                #     check if the latest_message is like "product XX is not available" where XX keeps changing
                    if "product" in latest_message and "not available" in latest_message:
                        # get the product name from the message
                        product_id = latest_message.split("product ")[1].split(" is not available")[0]
                        print(product_id)
                        # get the product id from the product name
                        # product_id = self.env['product.product'].search([('name', '=', product_name)])
                #       query stock_levels table to get the stock_available for the product
                        stock_available = self.env['stock.quant'].search([('product_id', '=', int(product_id))])
                        # for every entry in stock available, tract the location_id and quantity
                        message = ""
                        for stock in stock_available:
                            location_id = stock.location_id
                            quantity = stock.quantity
                            # if the location_id is the same as the location_id of the channel
                            # message = f'Product {product_id} is available in stock {stock_available}'
                            message = message + f'Product {product_id} is available in stock location id {location_id.id} in {quantity} quantity, \n'
                        latest_channel.with_user(copilot_user).message_post(body=message, message_type='comment',
                                                                                        subtype_xmlid='mail.mt_comment')
                        return rdata
                # bard_suggestions_channel.with_user(copilot_user).message_post(body=res, message_type='comment',
                #                                                               subtype_xmlid='mail.mt_comment')

                # ********************************************************************************************
                # code to simulate AI response manually
                if latest_message == "10 units of [E-COM07] Large Cabinet":
                    res = """<pre>
Thanks, follow my instructions
    
Check product availability in other warehouses
    Go to the inventory module
    Select Products
    Choose [E-COM07] Large Cabinet
    Click on the On Hand button on the top left of the product page
    See which warehouse has stock availability
    Decide who you want to ask the products from

Ask for approval
    Tag in this chat who needs to approve the transfer</pre>
                    """
                if latest_message == "@giovanni.ughi":
                    res = """<pre>
Approval
Hi @giovanni.ughi, location X needs 10 units of [E-COM07] Large Cabinet. Please approve the transfer.                    
</pre>"""
                if latest_message == "approved":
                    res = """<pre>
Thank you for the approval @giovann.ughi. Follow the below instructions to do an internal transfer
    Starting in the Inventory module, select Products
    Choose [E-COM07] Large Cabinet
    Click the Replenish button on the top left of the product page and fill out the pop-up form as follows:
        Quantity: the number of units that will be sent to the warehouse being replenished
        Scheduled Date: the date that the replenishment is scheduled to take place
        Warehouse: the warehouse that will be replenished
        Preferred Routes: select X: Supply Product from Y, with X being the warehouse to be replenished and Y being the warehouse that the product will be transferred from
Click Confirm and a delivery order will be created for the outgoing warehouse along with a receipt for the warehouse that will receive the product.
DONE
</pre>"""

                latest_channel.with_user(copilot_user).message_post(body=res, message_type='comment',
                                                                              subtype_xmlid='mail.mt_comment')

            except Exception as e:
                raise UserError(_(e))
        return rdata
