# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from functools import partial
from odoo.tools.misc import formatLang

class StockMove(models.Model):
    _inherit='stock.move'
    _order = 'picking_id, sequence, id'

    sequence = fields.Integer('Sequence', default=10)


    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[('type', 'in', ['product', 'consu'])], index=True, required=False,
        states={'done': [('readonly', True)]})

    product_uom = fields.Many2one('uom.uom', 'Unit of Measure', required=False)
    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        auto_join=True, index=True, required=False,
        help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations.")
    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location',
        auto_join=True, index=True, required=False,
        help="Location where the system will stock the finished products.")

    @api.model
    def create(self, values):
        if values.get('display_type', self.default_get(['display_type'])['display_type']):
            values.update(product_id=False,location_id=False,location_dest_id=False, product_uom_qty=0, product_uom=False)
        return super(StockMove, self).create(values)

    @api.multi
    def write(self, values):
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError(
                "You cannot change the type of a stock move line. Instead you should delete the current line and create a new line of the proper type.")
        return super(StockMove, self).write(values)

    @api.multi
    def unlink(self):
        for rec in self:
            if any(move.state not in ('draft', 'cancel') for move in rec):
                raise UserError(_('You can only delete draft moves.'))
            # With the non plannified picking, draft moves could have some move lines.
            for move in self.env['stock.move'].search([('picking_id','=',rec.picking_id.id)]):
                if move.display_type =='line_section':
                    move.state='cancel'
            for move in rec:
                if move.display_type =='line_section':
                    return True

            rec.mapped('move_line_ids').unlink()
            return super(StockMove, self).unlink()

class res_company(models.Model):
    _inherit = "res.company"

    fax=fields.Char('Fax')

class StockPicking(models.Model):
    _inherit='stock.picking'

    sale_order_id = fields.Many2one('sale.order', compute='_get_sale_order')
    vehicle_num=fields.Char('Vehicle Number')
    driver_id=fields.Many2one('hr.employee',string='Driver')

    @api.multi
    def button_validate(self):
        self.ensure_one()
        if self.move_ids_without_package.filtered(
                lambda m:m.display_type==False and( m.product_id.volume == 0 or m.product_id.weight == 0 or m.product_id.net_weight == 0)):
            pass
            # raise UserError(
            #     _('You have to define this product criteria (volume,weight,net weight) and it must not to be 0.'))
        for move in self.env['stock.move'].search([('picking_id', '=', self.id)]):
            if move.display_type == 'line_section':
                move.state = 'cancel'
        return super(StockPicking, self).button_validate()


    @api.depends('origin')
    def _get_sale_order(self):
        if self.origin:
            order = self.env['sale.order'].search(
                [
                    ('name', '=', self.origin),
                ],
                limit=1
            )

            self.sale_order_id=order.id


class ResPartner(models.Model):
    _inherit = "res.partner"

    main_contact=fields.Char('Main Contact')


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    net_weight = fields.Float(compute='_compute_weight', string='Net Weight(Kg)')
    gross_weight = fields.Float(compute='_compute_weight', string='Gross Weight(Kg)')
    account_bank_id = fields.Many2one('account.journal', string='Bank', required=True)

    @api.depends('invoice_line_ids')
    def _compute_weight(self):
        for account in self:
            net_weight=0
            gross_weight=0
            for line in account.invoice_line_ids:
                net_weight += line.product_id.net_weight * line.quantity
                gross_weight += line.product_id.weight * line.quantity
            account.gross_weight=gross_weight
            account.net_weight=net_weight



class ProductProduct(models.Model):
    _inherit = 'product.product'

    sae_id = fields.Many2one('product.sae',string='SAE')
    api_id = fields.Many2one('product.api',string='API')

class ProductSae(models.Model):
    _name='product.sae'

    name=fields.Char()


class ProductApi(models.Model):
    _name = 'product.api'

    name = fields.Char()
class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    other_ref =fields.Char('Other Reference(s)')
    despatch = fields.Char('Despatch')
    destination = fields.Char('Destination')


    @api.depends('amount_total')
    def _compute_amount_total_words(self):
        for order in self:
            order.amount_total_words = order.currency_id.amount_to_text(order.amount_total)

    amount_total_words = fields.Char("Total (In Words)", compute="_compute_amount_total_words")

class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery = fields.Char('Delivery')
    prices = fields.Char('Prices')
    type_of_oil=fields.Many2one('type.oil',string='Type Of Oil')
    ref=fields.Char('REF')
    joborder_note=fields.Text('Job Order Notes')
    account_bank_id=fields.Many2one('account.journal',string='Bank',required=True)

    @api.multi
    def print_job_order(self):
        return self.env.ref('armor_templates.action_report_joborder').report_action(self)

    def _prepare_invoice(self):
        """
        edit in _prepare invoice function of base to take my custom account_bank_id to account invoice
        """
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({'account_bank_id': self.account_bank_id.id })
        return res


class TypeOil(models.Model):
    _name = "type.oil"

    name=fields.Char()