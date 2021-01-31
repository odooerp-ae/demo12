# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import collections


class StockMove(models.Model):
    _inherit = 'stock.move'
    _order = "container_no"

    net_weight = fields.Float(compute='_compute_net_weight',string='Net Weight(Kg)')
    container_no = fields.Char(string='Container No.')
    volume = fields.Float(string='Volume(Liter)')
    gross_weight = fields.Float(compute='_compute_gross_weight',string='Gross Weight(Kg)')
    #seal_number = fields.Float('Seal No.')

    @api.depends('product_id','quantity_done')
    def _compute_net_weight(self):
        for stock in self:
            stock.net_weight = stock.product_id.net_weight * stock.quantity_done

    @api.depends('product_id', 'quantity_done')
    def _compute_gross_weight(self):
        for stock in self:
            stock.gross_weight = stock.product_id.weight * stock.quantity_done

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.update({
                'net_weight': self.product_id.net_weight * self.quantity_done,
                'volume': self.product_id.volume,
                'gross_weight': self.product_id.weight * self.quantity_done,
            })
            # self.container_no = self.product_id.container_no


class StockPicking(models.Model):
    _inherit = 'stock.picking'



    net_weight = fields.Float(
        string='Net Weight',
        compute='_compute_net_weight'
    )
    gross_weight = fields.Float(
        string='Gross Weight',
        compute='_compute_gross_weight'
    )
    unique_container_count = fields.Float(
        compute='_compute_unique_container',
        string='Unique Container Count'
    )
    #seal_number = fields.Float('Seal No.')

    '''
    @api.multi
    def button_validate(self):
        self.ensure_one()
        if self.move_ids_without_package.filtered(
                lambda m:m.display_type==False and( m.product_id.volume == 0 or m.product_id.weight == 0 or m.product_id.net_weight == 0)):
            raise UserError(
                _('You have to define this product criteria (volume,weight,net weight) and it must not to be 0.'))
        res=super(StockPicking, self).button_validate()
        return res
    '''

    @api.depends('move_lines.container_no')
    def _compute_unique_container(self):
        for stock in self:
            containers = stock.move_lines.mapped('container_no')
            stock.unique_container_count = len(list(set(containers)))

    @api.depends('move_lines.product_uom_qty', 'move_lines.net_weight')
    def _compute_net_weight(self):
        for stock in self:
            stock.net_weight = sum(stock.move_ids_without_package.mapped('net_weight')) or 0.0

    @api.depends('move_lines.product_uom_qty', 'move_lines.gross_weight')
    def _compute_gross_weight(self):
        for stock in self:
            stock.gross_weight = sum(stock.move_ids_without_package.mapped('gross_weight')) or 0.0


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        super(SaleOrder, self).action_confirm()
        for order in self:
            stock = self.env['stock.picking'].search(
                [
                    ('origin', '=', order.name),
                    ('group_id.name', '=', order.name)
                ],
                limit=1
            )
            #stock.sale_order_id= order
            for line in stock.move_lines.filtered(lambda ml: ml.product_id):
                line.write({
                    'net_weight': line.product_id.net_weight*line.quantity_done,
                    'volume': line.product_id.volume,
                    'gross_weight': line.product_id.weight*line.quantity_done,
                })
                # line.container_no = line.product_id.container_no
        return True

class ProductCategory(models.Model):
    _inherit = 'product.category'

    hs_code=fields.Char('Hs Code')