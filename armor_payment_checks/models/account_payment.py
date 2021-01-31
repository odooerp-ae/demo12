# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class AccountAbstractPayment(models.AbstractModel):
    _inherit = 'account.abstract.payment'

    partner_type = fields.Selection(selection_add=[('direct_account', 'Direct Account')])
    account_ids = fields.One2many('multi.payment.account', 'multi_payment_account', string='Multi Accounts')
    # amount = fields.Monetary(compute='_compute_paymnet_amount',store=True,string='Payment Amount', required=True)
    amount = fields.Monetary(required=False)
    bank_id = fields.Many2one(comodel_name="res.bank", string="Bank Name")
    debit_charges_account_id = fields.Many2one(comodel_name="account.account", string="Debit Charges Account", required=False, )
    debit_charges_amount = fields.Float(string="Debit Charges Amount")
    ref = fields.Char(string="Cheque No")
    due_date = fields.Date(string="Due Date")
    narration = fields.Text(string="Narration")

    @api.one
    @api.constrains('amount')
    def _check_amount(self):
        # print 'checksssss', self, self.amount, self.partner_type
        if not self.amount > 0.0 and self.partner_type != 'direct_account':
            raise ValidationError('The payment amount must be strictly positive.')

    @api.model
    def create(self, vals):
        # print 'in createeeeee', vals
        if 'partner_type' in vals and vals['partner_type'] == 'direct_account':
            accumalted_amount = 0.0
            if 'account_ids' in vals and vals['account_ids'] != []:
                for account in vals['account_ids']:
                    accumalted_amount += account[2]['amount']
                vals['amount'] = accumalted_amount
            else:
                raise UserError(_('You must enter at least one account in multi accounts.'))

        return super(AccountAbstractPayment, self).create(vals)

    @api.multi
    def write(self, vals):
        if self.partner_type == 'direct_account':
            accumalted_amount = 0.0
            nonupdated_lst = []
            if 'account_ids' in vals:
                for acc in vals['account_ids']:
                    if acc[2]:
                        if acc[2].get('amount'):
                            new_val = acc[2]['amount']
                            accumalted_amount += new_val
                        else:
                            # if we modified any field except the amount we will append the old one
                            for account in self.account_ids:
                                if account.id == acc[1]:
                                    accumalted_amount += account.amount
                    elif acc[0] != 2:  # case not delete
                        nonupdated_lst.append(acc[1])
                if nonupdated_lst:
                    for account in self.account_ids.filtered(lambda x: x.id in nonupdated_lst):
                        accumalted_amount += account.amount
                vals['amount'] = accumalted_amount
        return super(AccountAbstractPayment, self).write(vals)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    credit_journal_id = fields.Many2one(comodel_name="account.journal", string="Debit Journal",
                                        domain=[('type', 'in', ('bank', 'cash'))])
    journal_entries = fields.Many2one(comodel_name="account.move")
    deposit_count = fields.Integer(string="Deposit Count", compute="_count_deposit")
    rejected_count = fields.Integer(string="Rejected Count", compute="_count_reject")
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('sent', 'Sent'), ('deposit', 'Check Deposit'),
                              ('reject', 'Check Rejected'), ('reconciled', 'Reconciled')],
                             readonly=True, default='draft', copy=False, string="Status")
    journal_is_cheque = fields.Boolean(related="journal_id.is_cheque")
    journal_is_pdc = fields.Boolean(related="journal_id.pdc_issued")

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if not self.invoice_ids:
            # Set default partner type for the payment type
            if self.payment_type == 'inbound':
                self.partner_type = 'customer'
            elif self.payment_type == 'outbound':
                self.partner_type = 'supplier'
        # Set payment method domain
        res = self._onchange_journal()
        if not res.get('domain', {}):
           res['domain'] = {}
        res['domain']['journal_id'] = self.payment_type == 'inbound' and [('at_least_one_inbound', '=', True)] or [
            ('at_least_one_outbound', '=', True)]
        res['domain']['journal_id'].append(('type', 'in', ('bank', 'cash')))

        if self.payment_type == 'outbound':  # send vendor bill
            res['domain']['journal_id'].append(('is_cheque', '!=', True))
        elif self.payment_type == 'inbound':  # receive customer inv
            res['domain']['journal_id'].append(('pdc_issued', '!=', True))
        return res

    @api.onchange('partner_type')
    def _onchange_partner_type(self):
        if self.partner_type == 'direct_account':
            self.partner_id = ''

    @api.onchange('narration')
    @api.depends('move_line_ids')
    def _onchange_narration(self):
        if self.narration and self.move_line_ids:
            move_id = self.move_line_ids[0].move_id
            move_id.write({'ref': self.narration})
        elif self.move_line_ids:
            move_id = self.move_line_ids[0].move_id
            move_id.write({'ref': ""})

    @api.one
    def _count_deposit(self):
        # print len(self.env['account.move'].search([('payment_id', '=', self.id), ('ref', '=', 'deposited check')]))
        self.deposit_count = len(
            self.env['account.move'].search([('payment_id', '=', self.id), ('ref', '=', 'deposited check')]))

    @api.one
    def _count_reject(self):
        # print len(self.env['account.move'].search([('payment_id', '=', self.id), ('ref', '=', 'rejected check')]))
        self.rejected_count = len(
            self.env['account.move'].search([('payment_id', '=', self.id), ('ref', '=', 'rejected check')]))

    @api.multi
    def deposit_check(self):
        # raise Warning(self.credit_journal_id)
        self.ensure_one()
        if self.state != 'deposit':
            return {
                'name': 'Credit Journal Selection',
                'type': 'ir.actions.act_window',
                'res_model': 'account.payment.deposit.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                #  'context': {'default_due_date': ''}
            }
        else:
            raise ValidationError(
                'sorry this check has been already deposited before')

    @api.multi
    def reject_check(self):
        for check in self:
            if check.state == 'deposit':
                return {
                    'name': 'Credit Journal Selection',
                    'type': 'ir.actions.act_window',
                    'res_model': 'account.payment.reject.wizard',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'target': 'new',
                }
            else:
                raise ValidationError(
                    'sorry this check has been already Rejected before')

    @api.multi
    def reject_check_payment(self):
        # print 'in reject check'
        for check in self:
            if check.credit_journal_id and check.state == 'deposit':
                credit_journal = check.journal_entries
                reverse = credit_journal.reverse_moves()
                payment_move = check.env['account.move.line'].search([('payment_id', '=', check.id)], limit=1).mapped(
                    'move_id')
                payment_reverse = payment_move.reverse_moves()
                move = check.env['account.move'].search([('id', '=', reverse[0])])
                payment_move_reversed = check.env['account.move'].search([('id', '=', payment_reverse[0])])
                check.state = 'reject'
                check.credit_journal_id = False
                move.ref = "rejected check"
                payment_move_reversed.ref = "rejected check"
                payment_move_reversed.payment_id = check.id
                payment_move_line_reversed = check.env['account.move.line'].search(
                    [('move_id', '=', payment_move_reversed.id)])
                for line in payment_move_line_reversed:
                    line.payment_id = False

            elif check.state == 'reject':
                raise ValidationError('this check is already rejected')

    @api.multi
    def bulk_reject_cheque(self):
        for cheque in self:
            cheque.reject_check_payment()

    @api.multi
    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconciliable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:

            if rec.payment_type == 'inbound' and rec.partner_type != 'direct_account' and (not rec.debit_charges_account_id and not rec.debit_charges_amount):
                res = super(AccountPayment, self).post()
                if self.narration and self.move_line_ids:
                    self.move_line_ids[0].move_id.ref = self.narration
                return res

            if rec.state != 'draft':
                raise UserError(
                    _("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # Use the right sequence to set the name
            if rec.partner_type == 'direct_account':
                if rec.payment_type == 'inbound':
                    sequence_code = 'account.payment.direct.account.in'
                if rec.payment_type == 'outbound':
                    sequence_code = 'account.payment.direct.account.refund'
                    # if rec.payment_type == 'transfer':
                    # sequence_code = 'account.payment.direct.account.transfer'

                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(
                    sequence_code)

                # Create the journal entry
                amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)

                accumalted_amount = 0.0
                for account_obj in rec.account_ids:
                    accumalted_amount += account_obj.amount

                amount = accumalted_amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
                move = rec._create_payment_entry_custom(amount)

                move.ref = self.narration

                # In case of a transfer, the first journal entry created debited the source liquidity account and credited
                # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
                if rec.payment_type == 'transfer':
                    transfer_credit_aml = move.line_ids.filtered(
                        lambda r: r.account_id == rec.company_id.transfer_account_id)
                    transfer_debit_aml = rec._create_transfer_entry(amount)

                    (transfer_credit_aml + transfer_debit_aml).reconcile()

                # print 'accumalted_amount', accumalted_amount, amount
                rec.write({'state': 'posted', 'move_name': move.name, 'amount': accumalted_amount})

            if rec.partner_type != 'direct_account' and rec.debit_charges_account_id and  rec.debit_charges_amount:
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(
                    sequence_code)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

                    # Create the journal entry
                amount = rec.debit_charges_amount + rec.amount
                # Create the journal entry
                move = rec._create_payment_entry_other_charges(amount)
                rec.write({'state': 'posted', 'move_name': move.name})

    def _create_payment_entry_other_charges(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            #if all the invoices selected share the same currency, record the paiement in that currency too
            invoice_currency = self.invoice_ids[0].currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(self.amount, self.currency_id, self.company_id.currency_id, invoice_currency)

        move = self.env['account.move'].create(self._get_move_vals())

        #Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        print (counterpart_aml_dict , "==counterpart_aml_dict")
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        print ("--- counterpart_aml_dict",counterpart_aml_dict)
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)

        other_debit, other_credit, amount_currency, currency_id = aml_obj.with_context(
            date=self.payment_date).compute_amount_fields(self.debit_charges_amount, self.currency_id, self.company_id.currency_id,
                                                          invoice_currency)
        # Write line corresponding to invoice payment
        counterpart_aml_dict2 = self._get_shared_move_line_vals(other_debit, other_credit, amount_currency, move.id, False)
        print (counterpart_aml_dict2, "==counterpart_aml_dict2")
        counterpart_aml_dict2.update(self._get_counterpart_oher_charges_move_line_vals(self.invoice_ids))
        print ("--- counterpart_aml_dict2", counterpart_aml_dict2)
        counterpart_aml_dict2.update({'currency_id': currency_id})
        counterpart_aml2 = aml_obj.create(counterpart_aml_dict2)

        #Reconcile with the invoices
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)[2:]
            # the writeoff debit and credit must be computed from the invoice residual in company currency
            # minus the payment amount in company currency, and not from the payment difference in the payment currency
            # to avoid loss of precision during the currency rate computations. See revision 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
            total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.invoice_ids)
            total_payment_company_signed = self.currency_id.with_context(date=self.payment_date).compute(self.amount, self.company_id.currency_id)
            if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
                amount_wo = total_payment_company_signed - total_residual_company_signed
            else:
                amount_wo = total_residual_company_signed - total_payment_company_signed
            # Align the sign of the secondary currency writeoff amount with the sign of the writeoff
            # amount in the company currency
            if amount_wo > 0:
                debit_wo = amount_wo
                credit_wo = 0.0
                amount_currency_wo = abs(amount_currency_wo)
            else:
                debit_wo = 0.0
                credit_wo = -amount_wo
                amount_currency_wo = -abs(amount_currency_wo)
            writeoff_line['name'] = _('Counterpart')
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit']:
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit']:
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo
        self.invoice_ids.register_payment(counterpart_aml)

        #Write counterpart lines
        all_debit, all_credit, amount_currency, currency_id = aml_obj.with_context(
            date=self.payment_date).compute_amount_fields(self.debit_charges_amount+self.amount, self.currency_id,
                                                          self.company_id.currency_id,
                                                          invoice_currency)
        if not self.currency_id != self.company_id.currency_id:
            amount_currency = 0
        liquidity_aml_dict = self._get_shared_move_line_vals(all_credit, all_debit, -amount_currency, move.id, False)
        print (liquidity_aml_dict , "==== liquidity_aml_dict",liquidity_aml_dict)
        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
        print ("---- liquidity_aml_dict",liquidity_aml_dict)
        aml_obj.create(liquidity_aml_dict)

        move.post()
        return move

    def _get_counterpart_oher_charges_move_line_vals(self, invoice=False):
        if self.payment_type == 'transfer':
            name = self.name
        else:
            name = ''
            if self.partner_type == 'customer':
                if self.payment_type == 'inbound':
                    name += _("Customer Payment")
                elif self.payment_type == 'outbound':
                    name += _("Customer Refund")
            elif self.partner_type == 'supplier':
                if self.payment_type == 'inbound':
                    name += _("Vendor Refund")
                elif self.payment_type == 'outbound':
                    name += _("Vendor Payment")
            if invoice:
                name += ': '
                for inv in invoice:
                    if inv.move_id:
                        name += inv.number + ', '
                name = name[:len(name)-2]
        return {
            'name': name,
            'account_id': self.debit_charges_account_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
            'payment_id': self.id,
        }

    def _create_payment_entry_custom(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            # if all the invoices selected share the same currency, record the paiement in that currency too
            invoice_currency = self.invoice_ids[0].currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).\
            _compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)

        # print 'devbit,cre,amoo,cur', debit, credit, amount_currency, currency_id
        dict_created = self._get_move_vals()
        # print 'dict_created', dict_created
        move = self.env['account.move'].create(dict_created)

        main_credit = credit
        main_debit = debit
        # Write line corresponding to invoice payment
        for account in self.account_ids:
            if self.partner_type == 'direct_account' and self.payment_type == 'outbound':  # send money
                debit = account.amount
            elif self.partner_type == 'direct_account' and self.payment_type == 'inbound':  # send money
                credit = account.amount

            counterpart_aml_dict = self._get_shared_move_line_vals_custom(debit, credit, amount_currency, move.id,
                                                                          account.partner_id.id, False)
            print ('counterpart_aml_dict 1', counterpart_aml_dict, '========', account.account_id.id)
            dict_created2 = self._get_counterpart_move_line_vals_cutom(account, self.invoice_ids)
            print ('dict_created2 22', dict_created2)
            counterpart_aml_dict.update(dict_created2)
            counterpart_aml_dict.update({'currency_id': currency_id})
            print ('counterpart_aml_dict', counterpart_aml_dict)
            counterpart_aml = aml_obj.create(counterpart_aml_dict)
            print ('counterpart_aml', counterpart_aml)

        if self.partner_type != 'direct_account' and self.debit_charges_account_id and self.debit_charges_amount:
            debit = amount
            credit = 0.0
            credit_charges_amountt_aml_dict = self._get_shared_move_line_vals_custom(debit, credit, amount_currency, move.id,
                                                                                    self.partner_id.id, False)
            debit_charges_amountt_aml_dict = self._get_counterpart_move_line_vals_cutom(self.debit_charges_account_id, self.invoice_ids)
            credit_charges_amountt_aml_dict.update(debit_charges_amountt_aml_dict)
            credit_charges_amountt_aml_dict.update({'currency_id': currency_id})
            print ('credit_charges_amountt_aml_dict', credit_charges_amountt_aml_dict)
            counterpart_aml = aml_obj.create(credit_charges_amountt_aml_dict)
            print ('counterpart_aml', counterpart_aml)

        # Reconcile with the invoices
        # print ' self.payment_difference_handling', self.payment_difference_handling, self.payment_difference
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            print ('in enf iiiffffffffffffffff')
            writeoff_line = self._get_shared_move_line_vals_custom(0, 0, 0, move.id, False)
            debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(
                date=self.payment_date).compute_amount_fields(self.payment_difference, self.currency_id,
                                                              self.company_id.currency_id, invoice_currency)
            writeoff_line['name'] = _('Counterpart')
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit']:
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit']:
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo
        self.invoice_ids.register_payment(counterpart_aml)

        # Write counterpart lines
        if not self.currency_id != self.company_id.currency_id:
            amount_currency = 0
        liquidity_aml_dict = self._get_shared_move_line_vals_custom(main_credit, main_debit, -amount_currency, move.id,
                                                                    False, False)
        # print 'liquidity_aml_dict', liquidity_aml_dict
        liquidity_aml_dict.update(self._get_liquidity_move_line_vals_cutom(-amount))
        # print 'liquidity_aml_dict 2', liquidity_aml_dict
        aml_obj.create(liquidity_aml_dict)
        # print 'line2', aml_obj
        move.post()
        return move

    def _get_shared_move_line_vals_custom(self, debit, credit, amount_currency, move_id, partner_id, invoice_id=False):
        """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
        """
        return {
            'partner_id': partner_id or False,
            'invoice_id': invoice_id and invoice_id.id or False,
            'move_id': move_id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency or False,
            # 'date_maturity': account_line.due_date if account_line else self.payment_date ,
        }

    def _get_liquidity_move_line_vals_cutom(self, amount):
        name = self.name
        vals = {
            'name': name,
            'account_id': self.payment_type in ('outbound',
                                                'transfer') and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id,
            'payment_id': self.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }
        # If the journal has a currency specified, the journal item need to be expressed in this currency
        if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
            amount = self.currency_id.with_context(date=self.payment_date).compute(amount, self.journal_id.currency_id)
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(
                date=self.payment_date).compute_amount_fields(amount, self.journal_id.currency_id,
                                                              self.company_id.currency_id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })

        return vals

    def _get_counterpart_move_line_vals_cutom(self, account, invoice=False):
        if self.partner_type == 'direct_account':
            name = 'Direct Account_'
            name += account.name
            account_id = account.account_id.id
        else:
            name = 'Debit Charges Account_'
            name += account.name
            account_id = account.id
        return {
            'name': name,
            'account_id': account_id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
            'payment_id': self.id,
            'analytic_account_id': account.analytic_account_id.id if self.partner_type=='direct_account' else False
        }
