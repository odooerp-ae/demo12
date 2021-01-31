# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError


class AccountPaymentWizard(models.TransientModel):
    _name = 'account.payment.reject.wizard'

    due_date = fields.Date(string="Due Date")
    journal_id = fields.Many2one('account.journal', string='Payment Journal',
                                 domain=[('type', 'in', ('bank', 'cash'))])
    credit_journal_id = fields.Many2one('account.journal', string='Debit Journal',
                                        domain=[('type', 'in', ('bank', 'cash'))])

    @api.model
    def default_get(self, fields_list):
        res = {}
        active_id = self.env.context.get('active_id')
        current_payment = self.env['account.payment'].browse(active_id)

        res['journal_id'] = current_payment.journal_id.id
        res['credit_journal_id'] = current_payment.credit_journal_id.id
        res['due_date'] = current_payment.due_date

        return res

    @api.multi
    def reject(self):
        active_id = self.env.context.get('active_ids')
        current_payment = self.env['account.payment'].browse(active_id)
        for payment in current_payment:

            credit_journal = payment.journal_entries
            reverse = credit_journal.reverse_moves()
            payment_move = self.env['account.move.line'].search([('payment_id', '=', payment.id)], limit=1).mapped(
                                'move_id')
            payment_reverse = payment_move.reverse_moves()
            move = self.env['account.move'].search([('id', '=', reverse[0])])
            payment_move_reversed = self.env['account.move'].search([('id', '=', payment_reverse[0])])
            payment.write({"state": 'reject', 'credit_journal_id': False})
            move.write({"ref": 'rejected check'})
            payment_move_reversed.write({"ref": 'rejected check', 'payment_id': payment.id})

            payment_move_line_reversed = self.env['account.move.line'].search(
                [('move_id', '=', payment_move_reversed.id)])
            for line in payment_move_line_reversed:
                line.payment_id = False
                line.date_maturity = self.due_date

        return {'type': 'ir.actions.act_window_close'}
