# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp

class CheckMO(models.TransientModel):
    _name = "check.mo"

    name = fields.Char('Description', default="You will confirm this order without create manufacturing orders !!",required=False, translate=True)

    def action_continue(self):
       so =  self.env['sale.order'].browse(self.env.context.get('active_id'))
       so.message_post(body='This order Confirmed without Creating Any MO')
       return so.with_context(chk=True).action_confirm()