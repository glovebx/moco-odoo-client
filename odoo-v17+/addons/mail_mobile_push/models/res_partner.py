# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    mail_push_tokens = fields.One2many(
        "mail.push.token", "partner_id", string="Mobile push tokens")
