# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from pprint import pprint


class SalesPurchaseWizard(models.TransientModel):
    _name = "sales.purchase.report.wizard"
    _description = "Sale Purchase Report Wizard"

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
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
        return self.env.ref('ae_partner_report.sale_purchase_action_report').report_action(self, data=data)

class ReportSalesPurchase(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.ae_partner_report.sale_purchase_template_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        sale_state = data['form']['sale_state']
        purchase_state = data['form']['purchase_state']
        sale_purchase_check = data['form']['sale_purchase_check']
        partner_ids = data['form']['partner_ids']
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
                    docs.append({
                        'name': sale.name,
                        'date': sale.confirmation_date,
                        'partner': sale.partner_id.name,
                        'subtotal': sale.amount_untaxed,
                        'tax': sale.amount_tax,
                        'state': sale.state,
                    })
        else:
            if purchase_state:
                domain.append(('state', '=', purchase_state))

            domain.append(('date_order', '>=', date_from))
            domain.append(('date_order', '<=', date_to))
            purchase_ids = self.env['purchase.order'].search(domain)

            if purchase_ids:
                for purchase in purchase_ids:
                    docs.append({
                        'name': purchase.name,
                        'date': purchase.date_order,
                        'partner': purchase.partner_id.name,
                        'subtotal': purchase.amount_untaxed,
                        'tax': purchase.amount_tax,
                        'state': purchase.state,
                    })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_from': date_from,
            'date_to': date_to,
            'state': sale_purchase_check,
            'docs': docs,
        }
