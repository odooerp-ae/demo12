# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_shipment = fields.Selection(
        [
            ('1', 'Yes'),
            ('0', 'No')
        ],
        string='Shipment',
        required=True,
        default='0'
    )
    sale_order_id = fields.Many2one(
        'sale.order', string='Sale Order'
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        related='sale_order_id.analytic_account_id',
        string='Analytic Account',
        readonly=True
    )

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        if res.type == "in_invoice" and res.is_shipment == '1' and res.sale_order_id.analytic_account_id:
            res.invoice_line_ids.write({
                'account_analytic_id': res.sale_order_id.analytic_account_id.id
            })
        elif res.origin and res.type == "out_invoice":
            sale_order = self.env['sale.order'].search([('name', '=', res.origin)], limit=1)
            if sale_order:
                res.sale_order_id = sale_order.id
                '''
               for line in res.invoice_line_ids:
                   line.write({'account_analytic_id': salee_order.analytic_account_id.id})
               '''
        return res

    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(
            lambda inv: inv.state != 'open' and inv.type == "out_invoice" and inv.origin)
        if not to_open_invoices:
            return super(AccountInvoice, self).action_invoice_open()
        else:
            if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft']):
                raise UserError(
                    _("Invoice must be in draft or Pro-forma state in order to validate it."))

            lines = to_open_invoices.mapped('invoice_line_ids').filtered(
                lambda line:
                line.account_id.user_type_id and
                line.account_id.user_type_id.name in ['Income', 'Expenses']
            )
            lines.write({
                'account_analytic_id': to_open_invoices.analytic_account_id.id
            })

            to_open_invoices.action_date_assign()
            to_open_invoices.action_move_create()
            validated = to_open_invoices.invoice_validate()
            if to_open_invoices.move_id:
                move_lines = to_open_invoices.move_id.line_ids.filtered(
                        lambda l: l.account_id.user_type_id.name in ['Income', 'Expenses']
                )
                move_lines.write({
                    'account_analytic_id': to_open_invoices.analytic_account_id.id
                })
            return validated


'''
class AccountAnalyticLine(models.Model):
      _inherit='account.analytic.line'

      @api.model
      def create(self, vals):
          res = super(AccountAnalyticLine, self).create(vals)
          if not res.ref and res.move_id.journal_id.type =='purchase' and res.account_id != False:
              ref= res.move_id.move_id.name +'_'+ res.account_id.name
              res.write({'ref': ref})
          return res
'''


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    auto_sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True)
