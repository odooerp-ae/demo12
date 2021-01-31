# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from pprint import pprint


class ProductWizard(models.TransientModel):
    _name = "product.report.wizard"
    _description = "Product Report Wizard"

    date_from = fields.Date()
    date_to = fields.Date()
    sale_state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ])
    purchase_state = fields.Selection([
        ('draft', 'Draft RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ])
    sale_purchase_check = fields.Selection(selection=[('sale', _('Sales')), ('purchase', _('Purchase'))],default='sale')

    # Relational Fields
    partner_ids = fields.Many2many('res.partner')
    product_ids = fields.Many2many('product.product')

    # Avoid date from to be greater than date to
    @api.onchange('date_from','date_to')
    def change_date_from_to(self):
        if self.date_from and self.date_to:
            if self.date_to < self.date_from:
                raise UserError(_('Date from should not be greater than date to'))

    @api.multi
    def get_report(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'sale_state': self.sale_state,
                'purchase_state': self.purchase_state,
                'sale_purchase_check': self.sale_purchase_check,
                'partner_ids': self.partner_ids.ids,
                'product_ids': self.product_ids.ids,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
        return self.env.ref('ae_partner_report.product_action_report').report_action(self, data=data)


class ReportProduct(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.ae_partner_report.product_template_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        sale_state = data['form']['sale_state']
        purchase_state = data['form']['purchase_state']
        sale_purchase_check = data['form']['sale_purchase_check']
        partner_ids = data['form']['partner_ids']
        product_ids = data['form']['product_ids']
        domain = []
        docs = []

        if partner_ids:
            domain.append(('partner_id', 'in', partner_ids))

        if sale_purchase_check == 'sale':
            if sale_state:
                domain.append(('state', '=', sale_state))

            domain.append(('confirmation_date', '>=', date_from))
            domain.append(('confirmation_date', '<=', date_to))
            sale_ids = self.env['sale.order'].search(domain)
            if sale_ids:
                for sale in sale_ids:
                    if sale.order_line:
                        if product_ids:
                            for line in sale.order_line:
                                if line.product_id.id in product_ids:
                                    docs.append({
                                        'name': line.product_id.name,
                                        'partner': sale.partner_id.name,
                                        'order': sale.name,
                                        'qty': line.qty_delivered,
                                        'ordered_qty': line.product_uom_qty,
                                        'price': line.price_unit,
                                        'subtotal': line.price_subtotal,
                                    })
                        else:
                            for line in sale.order_line:
                                docs.append({
                                    'name': line.product_id.name,
                                    'partner': sale.partner_id.name,
                                    'order': sale.name,
                                    'qty': line.qty_delivered,
                                    'ordered_qty': line.product_uom_qty,
                                    'price': line.price_unit,
                                    'subtotal': line.price_subtotal,
                                })
        else:
            if purchase_state:
                domain.append(('state', '=', purchase_state))

            domain.append(('date_order', '>=', date_from))
            domain.append(('date_order', '<=', date_to))
            purchase_ids = self.env['purchase.order'].search(domain)

            if purchase_ids:
                for purchase in purchase_ids:
                    if purchase.order_line:
                        if product_ids:
                            for line in purchase.order_line:
                                if line.product_id.id in product_ids:
                                    docs.append({
                                        'name': line.product_id.name,
                                        'partner': purchase.partner_id.name,
                                        'order': purchase.name,
                                        'qty': line.qty_received,
                                        'ordered_qty': line.product_qty,
                                        'price': line.price_unit,
                                        'subtotal': line.price_subtotal,
                                    })

                        else:
                            for line in purchase.order_line:
                                docs.append({
                                    'name': line.product_id.name,
                                    'partner': purchase.partner_id.name,
                                    'order': purchase.name,
                                    'qty': line.qty_received,
                                    'ordered_qty': line.product_qty,
                                    'price': line.price_unit,
                                    'subtotal': line.price_subtotal,
                                })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_from': date_from,
            'date_to': date_to,
            'state': sale_purchase_check,
            'docs': docs,
        }