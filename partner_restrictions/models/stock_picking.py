# -*- coding: utf-8 -*-
""" Products to match bom"""
from odoo import fields, models, api, _
from odoo.tools import pycompat


class Picking(models.Model):
    _inherit = "stock.picking"

    def get_domain(self):
        user = self.env.user.id
        return [('user_id', '=', user)]

    partner_id = fields.Many2one('res.partner', domain=get_domain)
