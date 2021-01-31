from odoo import fields, models


class Company(models.Model):

    _inherit = "res.company"

    facebook = fields.Char()
    twitter = fields.Char()
    linkedin = fields.Char()
    instgram = fields.Char()
