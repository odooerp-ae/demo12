# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class MultiPaymentAccount(models.Model):
    _name = 'multi.payment.account'

    name = fields.Char(string='Label', required=True)
    account_id = fields.Many2one('account.account', string='Account', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=False,
                                 domain=[('customer', '=', False), ('supplier', '=', False)])
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    amount = fields.Float(string='Amount', required=True)
    multi_payment_account = fields.Many2one('account.abstract.payment')
    due_date = fields.Date(string="Due Date")


class AccountPaymentBulkDeposit(models.TransientModel):
    _name = 'account.payment.bulk.deposit'

    def _get_default_payment_type(self):
        account_payment = self.env['account.payment'].browse(self._context.get('active_ids', []))
        if account_payment:
            return account_payment[0].payment_type

    credit_journal_id = fields.Many2one(comodel_name="account.journal", string="Debit Journal", required=True,
                                        domain=[('type', 'in', ('bank', 'cash'))])
    payment_type = fields.Char(default=_get_default_payment_type)

    @api.multi
    def button_bulk_write(self):
        accounts_payment = self.env['account.payment'].browse(self._context.get('active_ids', []))
        for account_payment in accounts_payment:
            if account_payment.state == 'posted':
                self.bulk_write(account_payment, {'credit_journal_id': self.credit_journal_id.id,
                                                  'due_date': account_payment.due_date})
        return {'type': 'ir.actions.act_window_close'}

    def bulk_write(self, account_payment, vals):
        if vals.get('credit_journal_id'):
            credit_journal = self.env['account.journal'].search([('id', '=', vals['credit_journal_id'])])
            account_payment.state = 'deposit'
            credit = 0.0
            debit = 0.0
            if account_payment.payment_type == 'inbound':  # receive money
                credit = account_payment.amount
                debit = 0.0
            elif account_payment.payment_type == 'outbound':  # send money
                debit = account_payment.amount
                credit = 0.0
            move = self.env['account.move'].create({
                'name': account_payment.name,
                # 'partner_id':self.partner_type.id,
                'journal_id': credit_journal.id,
                'payment_id': account_payment.id,
                'date': vals.get('due_date') or datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
                'ref': "deposited check",
                'line_ids': [(0, 0, {
                    'name': 'check',
                    'debit': credit,
                    'credit': debit,
                    'account_id': credit_journal.default_debit_account_id.id,
                    'due_date': vals.get('due_date')
                }), (0, 0, {
                    'name': 'check',
                    'credit': credit,
                    'debit': debit,
                    'account_id': account_payment.journal_id.default_credit_account_id.id,
                    'due_date': vals.get('due_date')
                })]
            })
            move.post()
            move.name = credit_journal.sequence_id.next_by_id()
            account_payment.journal_entries = move
            account_payment.credit_journal_id = vals.get('credit_journal_id')
        return True


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_cheque = fields.Boolean(string="Pdc received", default=False)
    pdc_issued = fields.Boolean(string="PDC issued", default=False)

