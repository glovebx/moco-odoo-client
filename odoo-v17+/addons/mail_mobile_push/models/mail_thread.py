# -*- coding: utf-8 -*-

from markupsafe import Markup
import requests
import threading

from odoo import models, api, tools

import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

import logging as logger
_logger = logger.getLogger(__name__)

HMS_PUSH_GATEWAY = 'http://192.168.3.132:8069'


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        scheduled_date = self._is_notification_scheduled(kwargs.get('scheduled_date'))
        recipients_data = super(MailThread, self)._notify_thread(message, msg_vals=msg_vals, **kwargs)

        # if scheduled for later: notification queue will call the notification method
        if not scheduled_date:
            self._notify_thread_by_push(message, recipients_data, msg_vals, **kwargs)
        return recipients_data

    def _notify_thread_by_push(self, message, recipients_data, msg_vals=False, **kwargs):
        if not self.env['ir.config_parameter'].sudo().get_param('mail_mobile_push.enable_push'):
            return

        msg_vals = dict(msg_vals or {})
        pids = self._extract_partner_ids_for_notifications(message, msg_vals, recipients_data)

        if not pids:
            return

        self._notify_by_push_send(message, pids, msg_vals=msg_vals)

    def _notify_by_push_send(self, message, partner_ids, msg_vals=None):
        if not partner_ids:
            return

        if msg_vals is None:
            msg_vals = {}

        receiver_ids = self.env['res.partner'].sudo().browse(partner_ids).filtered(
            lambda r: len(r.mail_push_tokens.filtered(lambda t: t.platform == 'HMS')) > 0)
        if not receiver_ids:
            return

        # 找出所有 hms 的 token
        tokens = set()
        for receiver_id in receiver_ids:
            ts = receiver_id.mail_push_tokens.filtered(lambda t: t.platform == 'HMS').mapped('token')
            if len(ts) > 0:
                tokens.add(ts[0])
        payload = self._notify_by_push_prepare_payload(message, receiver_ids, msg_vals=msg_vals)

        threading.Thread(
            target=self._push_message,
            name="HMS message push",
            args=(payload, list(tokens), )
        ).start()

    def _push_message(self, payload, tokens):

        # 根据hms各式重新组合数据
        json_data = {
            'title': payload['author_name'],
            'body': payload['body'],
            'tokens': tokens,
        }

        try:
            # headers = {'Content-type': 'application/json'}
            requests.post(
                f"{HMS_PUSH_GATEWAY}/v1/hms/message/push",
                json=json_data,
                # headers=headers,
                timeout=5.0,
            )
        except Exception as e:
            _logger.error('An error occurred while contacting the gateway server: %s', e)

    def _notify_by_push_prepare_payload(self, message, receiver_ids, msg_vals=None):
        """
        组合通用数据
        """
        author_id = [msg_vals.get('author_id')] if 'author_id' in msg_vals else message.author_id.ids
        author_name = self.env['res.partner'].browse(author_id).name
        record_name = msg_vals.get('record_name') if msg_vals else message.record_name
        subject = msg_vals.get('subject') if msg_vals else message.subject
        body = msg_vals.get('body') if msg_vals else None
        if body and isinstance(body, Markup):
            body = body.unescape()
        user_ids = receiver_ids.mapped('user_ids').ids

        payload = {"author_name": author_name, "server_url": self.get_base_url(),
                   "db": self.env.cr.dbname, "user_ids": user_ids, 'subject': record_name or subject,
                   'body': body or subject, 'android_channel_id': 'Following'}

        return payload

    # 覆盖置空
    def _notify_thread_by_web_push(self, message, recipients_data, msg_vals=False, **kwargs):
        return
