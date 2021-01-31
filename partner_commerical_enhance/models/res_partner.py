# -*- coding: utf-8 -*-
import json
from lxml import etree
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    commercial_partner_id = fields.Many2one('res.partner',domain=lambda x:['&',('customer','=',True),'|',('user_id','=',x.env.user.id),('allowed_user_ids','in',x.env.user.id)])
