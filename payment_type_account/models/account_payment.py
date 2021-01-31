
# -*- coding: utf-8 -*-

from odoo import models, fields, api , _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date


class account_move_line(models.Model):
    _inherit = 'account.move.line'

    partner_id_account = fields.Many2one('account.account', string='Partner' , )
    is_account = fields.Boolean(string='Account' , default=False)

class account_payment(models.Model):
    _inherit = 'account.payment'



    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor') ,  ('accuont', 'Accounts')]) # , for fds , aps
    is_account = fields.Boolean(string='Account' , compute='onchange_partner_id' , default=False)
    partner_id_account = fields.Many2one('account.account', string='Account' , )
    temp = fields.Boolean(string='emp' , compute='get_account' , default=False)
    internal_cons = fields.Boolean(compute='comp_internal' , default=False)



    @api.depends('is_account' , 'payment_type')
    def comp_internal(self):
        if self.payment_type == 'transfer' or self.is_account : #or self.is_emp
            self.internal_cons = True


    @api.depends( 'partner_type') #'employee_id' ,
    def get_account(self):
        pass




    @api.model
    def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
        """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
        """
        return {
            'partner_id': self.partner_id.id or False,
            # 'partner_id_account' : self.partner_id_account.id  or False,
            'is_account' : self.is_account ,
            'invoice_id': invoice_id and invoice_id.id or False,
            'move_id': move_id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency or False,
            # 'account_id' : self.partner_id_account.id,
        }


    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id' , 'partner_id_account')
    def _compute_destination_account_id(self):
        if self.invoice_ids:
            self.destination_account_id = self.invoice_ids[0].account_id.id
        elif self.payment_type == 'transfer':
            if not self.company_id.transfer_account_id.id:
                raise UserError(_('Transfer account not defined on the company.'))
            if self.partner_type == 'accuont': # or self.partner_type == 'employee'
                self.destination_account_id = self.partner_id_account.id
                self.writeoff_account_id = self.partner_id_account.id
            else:
                self.destination_account_id = self.company_id.transfer_account_id.id
        elif self.partner_type == 'accuont':  #or self.partner_type == 'employee'
            self.destination_account_id = self.partner_id_account.id
            self.writeoff_account_id = self.partner_id_account.id


        elif self.partner_id:
            if self.partner_type == 'customer':
                self.destination_account_id = self.partner_id.property_account_receivable_id.id
            else:
                self.destination_account_id = self.partner_id.property_account_payable_id.id



    @api.one
    @api.depends('partner_type')
    def onchange_partner_id (self):

        if self.partner_type == 'accuont':
            self.is_account = True
        else :
            self.is_account = False



    def _get_liquidity_move_line_vals(self, amount):
        name = self.name
        if self.payment_type == 'transfer':
            name = _('Transfer to %s') % self.destination_journal_id.name
        if self.partner_type == 'accuont': # or self.partner_type == 'employee'
            vals = {
                'name': name,
                'account_id': self.partner_id_account.id,
                # 'account_id': self.payment_type in ('outbound',
                #                                     'transfer') and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id,
                'payment_id': self.id,
                'journal_id': self.journal_id.id,
                'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
            }

        else:

            vals = {
                'name': name,
                'account_id': self.payment_type in ('outbound','transfer') and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id,
                'payment_id': self.id,
                'journal_id': self.journal_id.id,
                'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
            }

        vals = {
            'name': name,
            'account_id': self.payment_type in ('outbound',
                                                'transfer') and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id,
            'payment_id': self.id,
            'journal_id': self.journal_id.id,
            'analytic_account_tag': [(6, 0, self.analytic_account_tag.ids)],
            'analytic_account_id': self.analytic_account.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }


        # If the journal has a currency specified, the journal item need to be expressed in this currency
        if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
            amount = self.currency_id.with_context(date=self.payment_date).compute(amount, self.journal_id.currency_id)
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(date=self.payment_date)._compute_amount_fields(amount, self.journal_id.currency_id, self.company_id.currency_id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })

        return vals



