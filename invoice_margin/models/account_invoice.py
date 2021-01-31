# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoiceInherit(models.Model):
    _inherit = 'account.invoice'

    margin_amount = fields.Float(string="Margin Amount",  required=False,compute='get_margin_amount',store=True )
    is_expense = fields.Boolean(string="Other Expense",  )
    account_invoice_line_ids = fields.Many2many(comodel_name="account.invoice.line", string="Other Expenses Bill", required=False, )
    total_expense_amount = fields.Float(string="Other Expense Cost",  required=False,compute='get_total_expense_amount',store=True )

    @api.multi
    @api.onchange('account_invoice_line_ids','invoice_line_ids','partner_id')
    def get_account_invoice_line(self):
        vendor_bill_lines = []
        invoice_lines = []
        bills = self.env['account.invoice'].search([('is_expense','=',True),('type','=','in_invoice')])
        invoices = self.env['account.invoice'].search([('is_expense','=',False),('type','=','out_invoice')])
        for bill_line in bills:
            for b_line in bill_line.invoice_line_ids:
                if b_line.product_id.type == 'service':
                    vendor_bill_lines.append(b_line.id)

        for inv_line in invoices:
            for in_line in inv_line.account_invoice_line_ids:
                invoice_lines.append(in_line.id)

        return {
            'domain':{'account_invoice_line_ids':[('id','in',vendor_bill_lines),('id','not in',invoice_lines)]}
        }





    @api.multi
    @api.depends('account_invoice_line_ids')
    def get_total_expense_amount(self):
        for rec in self:
            if rec.account_invoice_line_ids:
                for amount in rec.account_invoice_line_ids:
                    rec.total_expense_amount += amount.price_subtotal

    @api.multi
    @api.depends('account_invoice_line_ids','total_expense_amount','amount_untaxed')
    def get_margin_amount(self):
        for rec in self:
            rec.margin_amount = rec.amount_untaxed - rec.total_expense_amount


class AccountInvoiceLineInherit(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    @api.onchange('product_id','sequence')
    def get_product_expenses(self):
        for rec in self:
            products = []
            if rec.invoice_id.is_expense and rec.invoice_id.type == 'in_invoice':
                for prod in self.env['product.product'].search([('type','=','service')]):
                    products.append(prod.id)

                return {
                    'domain':{'product_id':[('id','in',products)]}
                }

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain_name = ['|', ('product_id', 'ilike', name),('invoice_id','ilike', name)]
        recs = self.search(domain_name + args, limit=limit)
        return recs.name_get()

    @api.multi
    def name_get(self):
        result = []
        for line in self:
            name = line.invoice_id.number or ''
            if line.product_id:
                name += ' / ' + str(line.product_id.name) + ' / ' + str(line.price_subtotal)

            result.append((line.id, name))
        return result


