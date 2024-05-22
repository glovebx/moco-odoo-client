# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_push = fields.Boolean('Enable Push Notifications', config_parameter='mail_mobile_push.enable_push')
