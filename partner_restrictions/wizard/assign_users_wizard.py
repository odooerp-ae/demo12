# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp

class LG(models.Model):
    _name = 'assign.user.wizard'
    _rec_name = 'name'
    name = fields.Char('Sequence',default='New')
    allowed_user_ids = fields.Many2many(comodel_name="res.users", string="Users", )
    def action_apply(self):
        for rec in self.env['res.partner'].search([('company_id','=',self.env.user.company_id.id)]):
            rec.allowed_user_ids=self.allowed_user_ids
    @api.model
    def create(self,vals):
        new_record = super(LG, self).create(vals)
        if len(self.search([]))>1:
            raise exceptions.ValidationError('You cannot define More than one record')
        return new_record

