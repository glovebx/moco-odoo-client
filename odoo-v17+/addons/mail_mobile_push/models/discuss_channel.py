# -*- coding: utf-8 -*-
from odoo import models


class DiscussChannel(models.Model):
    _inherit = 'discuss.channel'

    def _notify_thread_by_push(self, message, recipients_data, msg_vals=None, **kwargs):
        if not self.env['ir.config_parameter'].sudo().get_param('mail_mobile_push.enable_push'):
            return

        chat_channels = self.filtered(lambda channel: channel.channel_type == 'chat')
        if chat_channels:
            channel_rdata = recipients_data.copy()
            channel_rdata += [
                {'id': partner.id,
                 'share': partner.partner_share,
                 'active': partner.active,
                 'notif': 'push',
                 'type': 'customer',
                 'groups': [],
                }
                for partner in chat_channels.mapped("channel_partner_ids")
            ]
        else:
            channel_rdata = recipients_data

        return super()._notify_thread_by_push(message, channel_rdata, msg_vals=msg_vals, **kwargs)

    def _notify_by_push_prepare_payload(self, message, receiver_ids, msg_vals=None):
        payload = super()._notify_by_push_prepare_payload(message, receiver_ids, msg_vals=msg_vals)
        record_name = msg_vals.get('record_name') if msg_vals and 'record_name' in msg_vals else message.record_name
        if self.channel_type == 'chat':
            payload['subject'] = payload['author_name']
        elif self.channel_type == 'channel':
            payload['subject'] = "#%s - %s" % (record_name, payload['author_name'])
        else:
            payload['subject'] = "#%s" % (record_name)
        return payload
