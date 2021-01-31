# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    vendor_ids = fields.Many2many(comodel_name="res.partner", relation="requisition_vendor_rel", column1="requisition_id",
                                  column2="vendor_id", string="Vendors")

    @api.one
    def create_rfq(self):
        lines = []
        for line in self.line_ids:
            lines.append((0, 0,
              {'product_id': line.product_id.id, 'date_planned': line.schedule_date if line.schedule_date else fields.Date.today(),
               'product_qty': line.product_qty,
               'name': line.name,
               'product_uom': line.product_uom_id.id, 'price_unit': line.price_unit}))
        for vendor in self.vendor_ids:
            self.env['purchase.order'].create({'requisition_id':self.id,
                                               'order_line': lines,'partner_id': vendor.id})

    @api.multi
    def action_in_progress(self):
        if not all(obj.line_ids for obj in self):
            raise UserError(_('You cannot confirm Purchase Agreement because there is no product line.'))
        for record in self:
            vendor_ids = []
            product_lines = record.line_ids.mapped('product_id')
            for product in product_lines:
                vendor_ids += product.seller_ids.mapped('name').ids
            if record.vendor_ids:
                vendor_ids += record.vendor_ids.ids
            record.write({'state': 'in_progress', 'vendor_ids': [(6, 0, vendor_ids)]})

    @api.multi
    def action_open(self):
        for record in self:
            vendor_ids = []
            product_lines = record.line_ids.mapped('product_id')
            for product in product_lines:
                vendor_ids += product.seller_ids.mapped('name').ids
            if record.vendor_ids:
                vendor_ids += record.vendor_ids.ids

            record.write({'state': 'open', 'vendor_ids': [(6, 0, vendor_ids)]})

class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    name=fields.Char(string='Description')

    @api.onchange('product_id')
    def _onchange_product(self):
        super(PurchaseRequisitionLine,self)._onchange_product_id()
        if self.product_id:
            self.name=self.product_id.display_name
