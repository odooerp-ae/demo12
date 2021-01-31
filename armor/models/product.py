# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
import datetime

from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime

import pytz
class product(models.Model):
    _inherit = 'product.product'
    is_product_packaging = fields.Boolean(string="Is Packaging",  )
    bom_cost = fields.Float('Bom Cost')
class producttemplate(models.Model):
    _inherit = 'product.template'
    is_product_packaging = fields.Boolean(string="Is Packaging",  )
    bom_cost = fields.Float('Bom Cost')