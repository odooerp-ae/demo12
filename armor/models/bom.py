# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
import datetime

from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime

import pytz
class bom(models.Model):
    _inherit = 'mrp.bom'
    bom_type = fields.Selection(string="Type", selection=[('lube_raw', 'Lube(Raw)'),
                                                          ('packaging', 'Packaging'), ],
                                required=False, default='lube_raw')
    p_ids = fields.Many2many('product.product')
    @api.onchange('bom_type')
    def _compute_bom_type(self):
        self.bom_line_ids=False
        if self.bom_type=='packaging':
            self.p_ids = self.env['product.product'].search([('is_product_packaging','=',True)])
        else:
            self.p_ids = self.env['product.product'].search([('is_product_packaging', '=', False)])

    @api.constrains('bom_line_ids','bom_line_ids.perc')
    def _check_total_amount(self):
        if self.bom_type == 'lube_raw':
            if sum(self.bom_line_ids.mapped('product_qty')) != self.product_qty :
                raise exceptions.ValidationError('Total Raw Material Qty Must Be = Manufacture Qty')

class bom2(models.Model):
    _inherit = 'mrp.bom.line'
    perc = fields.Float('Percent')
    @api.onchange('perc')
    def onchange_perc(self):
        self.product_qty = self.perc/100*self.bom_id.product_qty


