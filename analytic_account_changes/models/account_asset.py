# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAsset(models.Model):
    _inherit = 'account.asset.asset'

    location = fields.Char(string="Location", required=False)
    serial_no = fields.Char(string="Serial No", required=False)
    notes = fields.Text(string="Notes")
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee")
    brand_id = fields.Many2one(comodel_name="account.asset.brand", string="Brand")
    model_id = fields.Many2one(comodel_name="account.asset.model", string="Model")


class AccountAssetBrand(models.Model):
    _name = 'account.asset.brand'
    _rec_name = 'name'

    name = fields.Char()


class AccountAssetModel(models.Model):
    _name = 'account.asset.model'
    _rec_name = 'name'

    name = fields.Char()
