# -*- coding: utf-8 -*-
""" Products to match bom"""
from odoo import fields, models, api, _
from odoo.tools import pycompat
class Crm(models.Model):
    _inherit = "crm.lead"
    partner_id = fields.Many2one('res.partner',domain=lambda x:['&',('customer','=',True),'|',('user_id','=',x.env.user.id),('allowed_user_ids','in',x.env.user.id)])

class Crm(models.Model):
    _inherit = "crm.team"

    @api.model
    def action_your_pipeline(self):
        res = super(Crm, self).action_your_pipeline()
        res['domain']=['|',('partner_id.user_id','=',self.env.user.id),('partner_id.user_id','in',self.env.user.allowed_user_ids.ids)]
        return res




