# -*- coding: utf-8 -*-
""" Products to match bom"""
from odoo import fields, models, api, _
from odoo.tools import pycompat

class CrmLead(models.Model):
    _inherit = "res.partner"

    phone2 = fields.Char(string='Phone 2')
    phone3 = fields.Char(string='Phone 3')
    email2 = fields.Char(string='Email 2')
    email3 = fields.Char(string='Email 3')

