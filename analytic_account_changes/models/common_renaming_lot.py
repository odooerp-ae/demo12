# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tracking = fields.Selection(
        [
            ('serial', 'By Unique Serial Number'),
            ('lot', 'By Batch No'),
            ('none', 'No Tracking')
        ],
        string="Tracking",
        default='none',
        required=True
    )


class StockMoveLots(models.Model):
    _inherit = 'stock.move.line'

    lot_id = fields.Many2one(
        'stock.production.lot',
        'Batch No',
        domain="[('product_id', '=', product_id)]"
    )
    lot_produced_id = fields.Many2one(
        'stock.production.lot',
        'Finished Batch No'
    )


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    final_lot_id = fields.Many2one(
        'stock.production.lot',
        'Current Batch No',
        domain="[('product_id', '=', product_id)]",
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}
    )


# class PackOperationLot(models.Model):
#     _inherit = "stock.pack.operation.lot"
#
#     lot_id = fields.Many2one(
#         'stock.production.lot',
#         'Batch No'
#     )
#     lot_name = fields.Char(
#         'Batch No'
#     )


# class StockPackOperation(models.Model):
#     _inherit = 'stock.pack.operation'
#
#     # override it to change form name to be batched no
#     @api.multi
#     def action_split_lots(self):
#         action_ctx = dict(self.env.context)
#         # If it's a returned stock move, we do not want to create a lot
#         returned_move = self.linked_move_operation_ids.mapped('move_id').mapped(
#             'origin_returned_move_id')
#         picking_type = self.picking_id.picking_type_id
#         action_ctx.update({
#             'serial': self.product_id.tracking == 'serial',
#             'only_create': picking_type.use_create_lots and not picking_type.use_existing_lots and not returned_move,
#             'create_lots': picking_type.use_create_lots,
#             'state_done': self.picking_id.state == 'done',
#             'show_reserved': any([lot for lot in self.pack_lot_ids if lot.qty_todo > 0.0])})
#         view_id = self.env.ref('stock.view_pack_operation_lot_form').id
#         return {
#             'name': _('Batch No Details'),
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'stock.pack.operation',
#             'views': [(view_id, 'form')],
#             'view_id': view_id,
#             'target': 'new',
#             'res_id': self.ids[0],
#             'context': action_ctx}
#
#     split_lot = action_split_lots


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    lot_id = fields.Many2one(
        'stock.production.lot',
        string='Batch No'
    )
