# -*- coding: utf-8 -*-
""" Products to match bom"""
from odoo import fields, models, api, _
from odoo.tools import pycompat

class Partner(models.Model):
    _inherit = "res.partner"
    @api.model
    def get_allowed_users(self):
        return self.env['assign.user.wizard'].search([],limit=1).allowed_user_ids
    allowed_user_ids  = fields.Many2many("res.users", 'allowedusr_rel', 'user_id', 'part_id',"Users TO access All partners",default=get_allowed_users )


