# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

from pprint import pprint

from datetime import timedelta, datetime
import calendar
import time

from odoo.exceptions import ValidationError, UserError, RedirectWarning
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import date_utils



class InvoicesBillsWizard(models.TransientModel):
    _name = "invoices.bills.report.wizard"
    _description = "Invoices Report Wizard"

    date_from = fields.Date()
    date_to = fields.Date()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], )
    invoices_bills_check = fields.Selection(selection=[('invoices', _('Invoices')), ('bills', _('Bills'))],
                                            default='invoices')

    # Relational Fields
    partner_ids = fields.Many2many('res.partner')

    # Avoid date from to be greater than date to
    @api.onchange('date_from', 'date_to')
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
                'state': self.state,
                'invoices_bills_check': self.invoices_bills_check,
                'partner_ids': self.partner_ids.ids,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
        return self.env.ref('ae_partner_report.invoices_bills_action_report').report_action(self, data=data)


class ReportInvoicesBills(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.ae_partner_report.invoices_bills_template_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        state = data['form']['state']
        invoices_bills_check = data['form']['invoices_bills_check']
        partner_ids = data['form']['partner_ids']
        domain = []
        docs = []

        domain.append(('date_invoice', '>=', date_from))
        domain.append(('date_invoice', '<=', date_to))

        if invoices_bills_check == 'invoices':
            domain.append(('type', '=', 'out_invoice'))
        else:
            domain.append(('type', '=', 'in_invoice'))

        if state:
            domain.append(('state', '=', state))

        if partner_ids:
            domain.append(('partner_id', 'in', partner_ids))

        invoice_ids = self.env['account.invoice'].search(domain)
        if invoice_ids:
            for invoice in invoice_ids:
                docs.append({
                    'invoice_number': invoice.number,
                    'date': invoice.date_invoice,
                    'partner': invoice.partner_id.name,
                    'subtotal': invoice.amount_untaxed,
                    'tax': invoice.amount_tax,
                    'amount_due': invoice.residual,
                    'state': invoice.state,
                })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_from': date_from,
            'date_to': date_to,
            'docs': docs,
        }

