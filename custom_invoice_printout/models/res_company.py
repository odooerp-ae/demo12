# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    invoice_report_template = fields.Many2one('ir.ui.view', 'Invoice Report')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('origin', 'company_id')
    def _get_related_delivery_order(self):
        for invoice in self:
            delivery_status = ''
            sale_order = self.env['sale.order'].search(
                [('name', 'ilike', invoice.origin), ('company_id', '=', invoice.company_id.id)])
            if sale_order:
                for order in sale_order:
                    for picking in sale_order.picking_ids:
                        delivery_status += picking.name
                    invoice.delivery_order_number = delivery_status
                    invoice.lpo_order_date = order.date_order
            else:
                purchase_order = self.env['purchase.order'].search(
                    [('name', 'ilike', invoice.origin), ('company_id', '=', invoice.company_id.id)])
                if purchase_order:
                    for order in purchase_order:
                        for picking in purchase_order.picking_ids:
                            delivery_status += picking.name
                        invoice.delivery_order_number = delivery_status
                        invoice.lpo_order_date = order.date_order

    lpo_customer_reference = fields.Char('Customer Reference')
    delivery_to = fields.Char('Delivery To')
    delivery_order_number = fields.Char(string='D.O No.', compute='_get_related_delivery_order')
    lpo_order_date = fields.Char(string='Date', compute='_get_related_delivery_order')
    vendor_do_number = fields.Char('Delivery oder reference')
