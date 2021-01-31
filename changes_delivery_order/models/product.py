# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    #net_weight = fields.Float(string='Net Weight')
    container_no = fields.Char(string='Container No.')
