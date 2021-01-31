from odoo import fields, models


class ArmorBrand(models.Model):
    _name = "armor.brand"

    name = fields.Char(string="Name")
    color = fields.Integer('Color', default=2)
