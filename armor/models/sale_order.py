# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
class Sale(models.Model):
    _inherit = 'sale.order'
    is_mo_confirmed=fields.Boolean('Is Mo Confirmed')
    def action_check_availability(self):

        for rec in self.order_line:
            if rec.product_id:
                rec.available_qty = rec.product_id.with_context({'warehouse' : rec.order_id.warehouse_id.id}).qty_available
                requested_qty = rec.product_uom._compute_quantity(rec.product_uom_qty, rec.product_id.uom_id)

                rec.mrp_qty = requested_qty-rec.available_qty
                if rec.mrp_qty<0:
                    rec.mrp_qty=0
    def confirm_mo(self):
        for line in self.order_line:
            if line.lube_mo:
                line.lube_mo.write({'is_draft': False})
            if line.packaging_mo:
                line.packaging_mo.write({'is_draft': False})
        self.is_mo_confirmed=True

    @api.multi
    def action_confirm(self):
        res = super(Sale, self).action_confirm()

        for rec in self.order_line:
            rec.action_create_lube_mo()
            rec.action_create_packaging_mo()
        self.confirm_mo()
        return res


    def open_manufacturing_orders(self):
        mo_ids = self.order_line.mapped('lube_mo') + self.order_line.mapped('packaging_mo')
        if mo_ids:
            if mo_ids.filtered(lambda c:c.is_draft==False):

                return {
                    'name': 'Draft MO',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'mrp.production',
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'context': {'create':False},
                    'domain':[('id','in',mo_ids.ids)]

                }
            else:
                raise exceptions.ValidationError(_('Please Click Button Confirm Mo First'))

        else:
            raise exceptions.ValidationError(_('There Is No Manufacturing Orders on this sale order'))

    # @api.multi
    # def action_confirm(self):
    #     if not self.env.context.get('chk'):
    #         if all(not x.lube_mo for x in self.order_line) and all(not y.packaging_mo for y in self.order_line):
    #             return {
    #                 'type': 'ir.actions.act_window',
    #                 'name': 'Check',
    #                 'res_model': 'check.mo',
    #                 'view_mode': 'form',
    #                 'view_type': 'form',
    #                 'target': 'new',
    #             }
    #         else:
    #             res = super(Sale, self).action_confirm()
    #             return res
    #     else:
    #         res = super(Sale, self).action_confirm()
    #         return res
class NewModule(models.Model):
    _inherit = 'sale.order.line'
    available_qty = fields.Float(string="Available Qty",  required=False, )
    mrp_qty = fields.Float(string="Mrp Qty",  required=False, )
    lube_mo = fields.Many2one('mrp.production')
    packaging_mo = fields.Many2one('mrp.production')
    lub_bom_id = fields.Many2one('mrp.bom','Lube(Raw) BOM')
    pack_bom_id = fields.Many2one('mrp.bom','Packaging BOM')
    prod_tmpl_id = fields.Many2one('product.template',related='product_id.product_tmpl_id',store=True)
    @api.onchange('product_id')
    def onchng_product(self):
            if self.product_id:
                return {'domain':{'lub_bom_id':[('id','in',self.product_id.bom_ids.filtered(lambda x: x.bom_type == 'lube_raw').ids)],
                                  'pack_bom_id':[('id','in',self.product_id.bom_ids.filtered(lambda x: x.bom_type == 'packaging').ids)]}}
            else:
                return {'domain':{'lub_bom_id':[('id','=',False)],'pack_bom_id':[('id','=',False)],
                                  }}
    @api.onchange('product_uom_qty')
    def onchange_product_id_get_qty(self):
        for rec in self:
                requested_qty = rec.product_uom._compute_quantity(rec.product_uom_qty, rec.product_id.uom_id)
                rec.mrp_qty = requested_qty-rec.available_qty
                if rec.mrp_qty<0:
                    rec.mrp_qty=0

    def action_create_lube_mo(self):
        if not self.lube_mo:
            bom = self.product_id.bom_ids.filtered(lambda x: x.bom_type == 'lube_raw')
            if not bom :
                raise exceptions.ValidationError("This product don't have Lube(Raw) BOM")
            if not self.lub_bom_id:
                raise exceptions.ValidationError("Select Lube(Raw) BOM")
            # bom =bom[0]
            seq = self.env['ir.sequence'].next_by_code('mrp.production') or _('New')
            cr_id = self.env['mrp.production'].create({'name': seq,
                                                       'product_id': self.product_id.id,
                                                       'product_qty': self.mrp_qty,
                                                       'bom_id': self.lub_bom_id.id,
                                                       'mo_type': 'lube_raw',
                                                       'is_draft': True,
                                                       'product_uom_id': self.product_uom.id
                                                       })
            self.lube_mo=cr_id.id
        view_id = self.env.ref('armor.mrp_production_form_view2').id
        context = self._context.copy()
        return {
        'name': 'Draft MO',
        'view_mode': 'tree',
        'views': [(view_id, 'form')],
        'res_model': 'mrp.production',
        'view_id': view_id,
        'type': 'ir.actions.act_window',
        'res_id': self.lube_mo.id,
        'target': 'new',
        'context': context,

    }
    def action_create_packaging_mo(self):
        if not self.packaging_mo:
            bom = self.product_id.bom_ids.filtered(lambda x: x.bom_type == 'packaging')
            if not bom:
                raise exceptions.ValidationError("This product don't have Packaging BOM")
            if not self.pack_bom_id:
                raise exceptions.ValidationError("Select Packaging BOM")
            bom = bom[0]
            seq = self.env['ir.sequence'].next_by_code('mrp.production') or _('New')
            cr_id = self.env['mrp.production'].create({'name': seq,
                                                       'product_id': self.product_id.id,
                                                       'product_qty': self.mrp_qty,
                                                       'bom_id': self.pack_bom_id.id,
                                                       'mo_type': 'packaging',
                                                       'is_draft': True,
                                                       'product_uom_id': self.product_uom.id
                                                       })
            self.packaging_mo = cr_id.id
        view_id = self.env.ref('armor.mrp_production_form_view2').id
        context = self._context.copy()
        return {
            'name': 'MO',
            'view_mode': 'tree',
            'views': [(view_id, 'form')],
            'res_model': 'mrp.production',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': self.packaging_mo.id,
            'target': 'new',
            'context': context,

        }
