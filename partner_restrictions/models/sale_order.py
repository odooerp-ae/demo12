# -*- coding: utf-8 -*-
""" Products to match bom"""
from odoo import fields, models, api, _
from odoo.tools import pycompat
from odoo.tools.safe_eval import safe_eval

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def get_domain(self):
        user = self.env.user.id
        return [('user_id', '=', user)]

    partner_id = fields.Many2one('res.partner', domain=get_domain)

