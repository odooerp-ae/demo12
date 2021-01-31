# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round
from odoo.fields import Date, Datetime
import datetime
from dateutil.relativedelta import relativedelta

class Manufacturing(models.Model):
    _inherit = 'mrp.production'
    mo_type = fields.Selection(string="Type", selection=[('lube_raw', 'Lube(Raw)'),
                                                         ('packaging', 'Packaging'), ],
                               required=False, default='lube_raw')
    is_draft = fields.Boolean('Is Draft')

    @api.multi
    def _generate_moves(self):
        for production in self:
            production._generate_finished_moves()
            factor = production.product_uom_id._compute_quantity(production.product_qty,
                                                                 production.bom_id.product_uom_id) / production.bom_id.product_qty
            boms, lines = production.bom_id.explode(production.product_id, factor,
                                                    picking_type=production.bom_id.picking_type_id)
            production._generate_raw_moves(lines)
            production._adjust_procure_method()
        return True

    @api.multi
    def action_assign(self):
        for rec in self:
            rec.move_raw_ids.filtered(lambda x:x.state == 'draft')._action_confirm()
        return super(Manufacturing, self).action_assign()

class MrpWorkOrder(models.Model):
    _inherit = 'mrp.workorder'
    @api.multi
    def record_production(self):
        result = super(MrpWorkOrder, self).record_production()
        raw_moves1 = self.move_raw_ids.filtered(
            lambda x: (x.has_tracking == 'none') and (
                    x.state not in (
                'done', 'cancel'))  and x.workorder_id)  # and x.bom_line_id
        for rec in raw_moves1:
                rec.write({'quantity_done': rec.product_uom_qty})
        return result
