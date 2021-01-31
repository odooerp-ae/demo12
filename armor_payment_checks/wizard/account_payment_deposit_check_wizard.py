# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class AccountPaymentWizard(models.TransientModel):
    _name = 'account.payment.deposit.wizard'

    due_date = fields.Date(string="Due Date")
    journal_id = fields.Many2one('account.journal', string='Payment Journal', domain=[('type', 'in', ('bank', 'cash'))])
    credit_journal_id = fields.Many2one('account.journal', string='Debit Journal',
                                        domain=[('type', 'in', ('bank', 'cash'))])

    @api.model
    def default_get(self, fields_list):
        res = {}
        active_id = self.env.context.get('active_id')
        current_payment=self.env['account.payment'].browse(active_id)
        res['journal_id'] = current_payment.journal_id.id
        res['due_date'] = current_payment.due_date

        return res

    @api.multi
    def deposit(self):
        credit_journal = self.env['account.journal'].search([('id', '=', self.credit_journal_id.id)])
        active_id = self.env.context.get('active_ids')
        current_payment = self.env['account.payment'].browse(active_id)
        for payment in current_payment:
            # journal_id = payment.journal_id.id
            payment.write({'state': 'deposit', 'credit_journal_id': self.credit_journal_id.id})
            credit = 0.0
            debit = 0.0
            if payment.payment_type == 'inbound':  # receive money
                credit = payment.amount
                debit = 0.0
            elif payment.payment_type == 'outbound':  # send money
                debit = payment.amount
                credit = 0.0

            move = self.env['account.move'].create({
                'name': payment.name,
                # 'partner_id':self.partner_type.id,
                'journal_id': credit_journal.id,
                'payment_id': payment.id,
                'date': self.due_date or datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
                'ref': "deposited check",
                'line_ids': [(0, 0, {
                    'name': 'check',
                    'debit': credit,
                    'credit': debit,
                    'account_id': credit_journal.default_debit_account_id.id,
                    'due_date': self.due_date
                }), (0, 0, {
                    'name': 'check',
                    'credit': credit,
                    'debit': debit,
                    'account_id': self.journal_id.default_credit_account_id.id,
                    'due_date': self.due_date
                })]
            })
            move.post()
            move.name = credit_journal.sequence_id.next_by_id()
            payment.journal_entries = move
        return {'type': 'ir.actions.act_window_close'}
