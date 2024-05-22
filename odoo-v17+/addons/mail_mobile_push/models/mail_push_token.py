# -*- coding: utf-8 -*-
from odoo import fields, models, api


class MailPushToken(models.Model):
    _name = "mail.push.token"
    _description = 'Push Tokens table for odoo'

    partner_id = fields.Many2one('res.partner', string="Partner", readonly=False)
    token = fields.Char(string="Device push token", readonly=False)
    platform = fields.Char(string="Device platform", readonly=False, help="HMS、GMS")

    _sql_constraints = [
        ('token', 'unique(token, platform, partner_id)', 'Token must be unique per partner!'),
        ('token_not_false', 'CHECK (token IS NOT NULL)', 'Token must be not null!'),
    ]

    # @api.model
    # def get_platform_token(self, platform):
    #     platform_tokens = self.env.user.partner_id.mail_push_tokens.filtered(lambda t: t.platform == platform)
    #     return platform_tokens[0].token if platform_tokens else None

    @api.model
    def register_platform_token(self, platform, token):
        platform_tokens = self.env.user.partner_id.mail_push_tokens.filtered(lambda t: t.platform == platform)
        if platform_tokens.filtered(lambda t: t.token == token):
            # already exists
            return True

        platform_tokens.filtered(lambda t: t.token != token).unlink()
        self.env.user.partner_id.write(
            {'mail_push_tokens': [(0, 0, {'platform': platform, 'token': token})]})
        return True
