from openerp import models, fields, api
''' To add more fields to bank account.'''


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    baneficiary_name = fields.Char("Baneficiary Name")
    iban = fields.Char("IBAN")
    branch = fields.Char("Branch")
    swift = fields.Char("SWIFT")
    display_on_report = fields.Boolean(string="Display On report")