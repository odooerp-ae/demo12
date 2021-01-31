# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
                                          readonly=True,)

    @api.multi
    def action_confirm(self):
        super(SaleOrder, self).action_confirm()
        for order in self:
            analytic_account = self.env['account.analytic.account'].create(
                {
                    'name': _('analytic_account_') + order.name,
                    'partner_id': order.partner_id.id,
                    'code': order.name,
                    'auto_sale_order_id': order.id
                }
            )
            order.write({
                'analytic_account_id': analytic_account.id
            })

            break
        return True
