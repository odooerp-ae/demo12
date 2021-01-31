# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AddProductSale(models.TransientModel):
    _name = 'sale.order.product'

    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=False, )
    category_id = fields.Many2one(comodel_name="product.category", string="Product Category", required=False, )
    search_pd = fields.Char(string="Search Name", required=False, )
    search_pd2 = fields.Char(string="Internal Ref", required=False, )
    product_ids = fields.Many2many(comodel_name='sale.product.first', string='Search Products')
    final_product_ids = fields.Many2many(comodel_name='sale.product.final', string='Final Products',store=True)
    price_unit = fields.Float(string="Unit Price",  required=False, )

    @api.onchange('search_pd','search_pd2', 'category_id')
    def search_char(self):
        print ('[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[kkkkkkkkk')
        # self.env['sale.product.first'].search([]).unlink()
        self.product_ids = False
        products = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
        products_with_pd = self.env['product.product'].search(
            ['|',('name', 'ilike', self.search_pd),('default_code', 'ilike', self.search_pd2)])

        data = []


        if self.category_id and not self.search_pd and not self.search_pd2:
            for prod in products:
                line = self.env['sale.product.first'].create({
                    'product_id': prod.id,
                    'partner_id': self.partner_id.id})
                data.append(line.id)
            self.product_ids = data

        if self.category_id and (self.search_pd or self.search_pd2):
            print('xxxxxxxxxxxxxxx')
            for prod in products_with_pd:
                print('ccccccccccc')
                if prod.categ_id.id == self.category_id.id:
                    line = self.env['sale.product.first'].create({
                        'product_id': prod.id,
                        'partner_id': self.partner_id.id})
                    data.append(line.id)
            self.product_ids = data


        if not self.category_id and (self.search_pd or self.search_pd2):
            print ('kkkkkkkkkk')
            for prod in self.env['product.product'].search(
            ['|', ('name', 'ilike', self.search_pd), ('default_code', 'ilike', self.search_pd2)]):
                print('ccccccccccc')
                # if prod.categ_id.id == self.category_id.id:
                line = self.env['sale.product.first'].create({
                    'product_id': prod.id,
                    'partner_id': self.partner_id.id})
                data.append(line.id)
            self.product_ids = data

    @api.onchange('product_ids','product_ids.choose','product_ids.quantity')
    def search_product(self):
        data = [line.id for line in self.env['sale.product.final'].search([])]
        products = [line.product_id.id for line in self.env['sale.product.final'].search([])]
        for line in self.product_ids.filtered(lambda c: c.choose and c.quantity):
            if line.product_id.id not in products:
                final_line = self.env['sale.product.final'].create({
                    'product_id': line.product_id.id,
                    # 'module_id': line.module_id.id,
                    'quantity': line.quantity,
                    # 'discount': line.discount,
                })
                data.append(final_line.id)
            else:
                for product in self.final_product_ids:
                    if product.product_id.id == line.product_id.id:
                        product.update({
                            'product_id': line.product_id.id,
                            # 'module_id': line.module_id.id,
                            'quantity': line.quantity,
                            # 'discount': line.discount,
                        })
                        break

        self.final_product_ids = data
        return {'type': 'ir.actions.act_window_open'}

    @api.multi
    def get_final_product(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            run_data = self.env['sale.order'].browse(active_id)
        if not self.env['sale.product.final'].search([]):
            raise UserError(_("You must add product(s) to generate sale order(s)."))
        for product in self.env['sale.product.final'].search([]):
            res = {
                'order_id': active_id,
                'product_id': product.product_id.id,
                # 'modules_name_id': product.module_id.id,
                'name': product.product_id.name,
                'price_unit': product.product_id.lst_price,
                'product_uom_qty': product.quantity,
            }
            run_data.write({'order_line': [(0, 0, res)]})
        self.env['sale.product.final'].search([]).unlink()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def cancel_product(self):
        self.env['sale.product.final'].search([]).unlink()
        return {'type': 'ir.actions.act_window_close'}


class AddProductPurchase(models.TransientModel):
    _name = 'purchase.order.product'

    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=False, )
    category_id = fields.Many2one(comodel_name="product.category", string="Product Category", required=False, )
    search_pd = fields.Char(string="Search Name", required=False, )
    search_pd2 = fields.Char(string="Internal Ref", required=False, )
    product_ids = fields.Many2many(comodel_name='purchase.product.first', string='Search Products')
    final_product_ids = fields.Many2many(comodel_name='purchase.product.final', string='Final Products', store=True)

    @api.multi
    def cancel_product(self):
        self.env['purchase.product.final'].search([]).unlink()
        return {'type': 'ir.actions.act_window_close'}

    @api.onchange('search_pd','search_pd2', 'category_id')
    def search_char(self):
        # self.env['purchase.product.first'].search([]).unlink()
        self.product_ids = False
        products = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
        products_with_pd = self.env['product.product'].search(
            ['|',('name', 'ilike', self.search_pd),('default_code', 'ilike', self.search_pd2)])
        data = []
        if self.category_id and not self.search_pd and not self.search_pd2:
            for prod in products:
                line = self.env['purchase.product.first'].create({
                    'product_id': prod.id,
                    'partner_id': self.partner_id.id})
                data.append(line.id)
            self.product_ids = data

        if self.category_id and (self.search_pd or self.search_pd2):
            print('vvvvvvvvvvvvvvvvv')
            for prod in products_with_pd:
                print('bbbbbbbbbbbbbb')
                if prod.categ_id.id == self.category_id.id:

                    line = self.env['purchase.product.first'].create({
                        'product_id': prod.id,
                        'partner_id': self.partner_id.id})
                    data.append(line.id)
                    print(data,'oooooooooooooo')
            self.product_ids = data

        if not self.category_id and (self.search_pd or self.search_pd2):
            print ('kkkkkkkkkk')
            for prod in self.env['product.product'].search(
            ['|', ('name', 'ilike', self.search_pd), ('default_code', 'ilike', self.search_pd2)]):
                print('bbbbbbbbbbbbbb')
                # if prod.categ_id.id == self.category_id.id:

                line = self.env['purchase.product.first'].create({
                    'product_id': prod.id,
                    'partner_id': self.partner_id.id})
                data.append(line.id)
                print(data,'oooooooooooooo')
            self.product_ids = data



    @api.onchange('product_ids')
    def search_product(self):
        data = [line.id for line in self.env['purchase.product.final'].search([])]
        products = [line.product_id.id for line in self.env['purchase.product.final'].search([])]
        for line in self.product_ids.filtered(lambda c: c.choose and c.quantity):
            if line.product_id.id not in products:
                final_line = self.env['purchase.product.final'].create({
                    'product_id': line.product_id.id,
                    # 'module_id': line.module_id.id,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                })
                data.append(final_line.id)

            else:
                for product in self.final_product_ids:
                    if product.product_id.id == line.product_id.id:
                        product.update({
                            'product_id': line.product_id.id,
                            # 'module_id': line.module_id.id,
                            'quantity': line.quantity,
                            'price_unit': line.price_unit,
                        })
                        break
        self.final_product_ids = data
        return {'type': 'ir.actions.act_window_open'}

    @api.multi
    def get_final_product(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            run_data = self.env['purchase.order'].browse(active_id)
        if not self.env['purchase.product.final'].search([]):
            raise UserError(_("You must add product(s) to generate purchase order(s)."))
        for product in self.env['purchase.product.final'].search([]):
            res = {
                'order_id': active_id,
                'product_id': product.product_id.id,
                'date_planned': run_data.date_planned,
                # 'shipment_date': run_data.shipment_date,
                # 'arrival_date': run_data.arrival_date,
                'product_uom': product.product_id.uom_id.id,
                'price_unit': product.price_unit,
                # 'modules_name_id': product.module_id.id,
                'name': product.product_id.name,
                'product_qty': product.quantity,
            }
            run_data.write({'order_line': [(0, 0, res)]})
        self.env['purchase.product.final'].search([]).unlink()
        return {'type': 'ir.actions.act_window_close'}


# class AddProduct_Purchase_Request(models.TransientModel):
#     _name = 'requests.order.product'
#
#     # partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=False, )
#     category_id = fields.Many2one(comodel_name="product.category", string="Product Category", required=False, )
#     search_pd = fields.Char(string="Search Name", required=False, )
#     search_pd2 = fields.Char(string="Internal Ref", required=False, )
#     product_ids = fields.Many2many(comodel_name='purchase.request.product.first', string='Search Products')
#     final_product_ids = fields.Many2many(comodel_name='purchase.request.product.final', string='Final Products',
#                                          store=True)
#
#     @api.multi
#     def cancel_product(self):
#         self.env['purchase.request.product.final'].search([]).unlink()
#         return {'type': 'ir.actions.act_window_close'}
#
#     @api.onchange('search_pd','search_pd2', 'category_id')
#     def search_char(self):
#         # self.env['purchase.request.product.first'].search([]).unlink()
#         self.product_ids = False
#         products = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
#         products_with_pd = self.env['product.product'].search(
#             ['|',('name', 'ilike', self.search_pd),('default_code', 'ilike', self.search_pd2)])
#         data = []
#         if self.category_id and not self.search_pd and not self.search_pd2:
#             for prod in products:
#                 line = self.env['purchase.request.product.first'].create({
#                     'product_id': prod.id})
#                 data.append(line.id)
#             self.product_ids = data
#         if self.category_id and (self.search_pd or self.search_pd2):
#             print('nnnnnnnnnnnnnnnnnn')
#             for prod in products_with_pd:
#                 print('mmmmmmmmmmmmmmmmm')
#                 if prod.categ_id.id == self.category_id.id:
#                     line = self.env['purchase.request.product.first'].create({
#                         'product_id': prod.id})
#                     data.append(line.id)
#             self.product_ids = data
#
#     @api.onchange('product_ids')
#     def search_product(self):
#         data = [line.id for line in self.env['purchase.request.product.final'].search([])]
#         products = [line.product_id.id for line in self.env['purchase.request.product.final'].search([])]
#         for line in self.product_ids.filtered(lambda c: c.choose and c.quantity):
#             if line.product_id.id not in products:
#                 final_line = self.env['purchase.request.product.final'].create({
#                     'product_id': line.product_id.id,
#                     'module_id': line.module_id.id,
#                     'quantity': line.quantity,
#                 })
#                 data.append(final_line.id)
#             else:
#                 for product in self.final_product_ids:
#                     if product.product_id.id == line.product_id.id:
#                         product.update({
#                             'product_id': line.product_id.id,
#                             'module_id': line.module_id.id,
#                             'quantity': line.quantity,
#                         })
#                         break
#         self.final_product_ids = data
#         return {'type': 'ir.actions.act_window_open'}
#
#     @api.multi
#     def get_final_product(self):
#         active_id = self.env.context.get('active_id')
#         if active_id:
#             run_data = self.env['purchase.requisition'].browse(active_id)
#         if not self.env['purchase.request.product.final'].search([]):
#             raise UserError(_("You must add product(s) to generate purchase order(s)."))
#         for product in self.env['purchase.request.product.final'].search([]):
#             res = {
#                 'requisition_id': active_id,
#                 'product_id': product.product_id.id,
#
#                 'product_uom_id': product.product_id.uom_id.id,
#                 'price_unit': product.product_id.standard_price,
#                 'modules_name_id': product.module_id.id,
#                 'name': product.product_id.name,
#                 'product_qty': product.quantity,
#             }
#             run_data.write({'line_ids': [(0, 0, res)]})
#         self.env['purchase.request.product.final'].search([]).unlink()
#         return {'type': 'ir.actions.act_window_close'}
#
#
class AddProduct_material_request(models.TransientModel):
    _name = 'material.request.product'

    category_id = fields.Many2one(comodel_name="product.category", string="Product Category", required=False, )
    search_pd = fields.Char(string="Search Name", required=False, )
    search_pd2 = fields.Char(string="Internal Ref", required=False, )
    product_ids = fields.Many2many(comodel_name='material.request.product.first', string='Search Products')
    final_product_ids = fields.Many2many(comodel_name='material.request.product.final', string='Final Products',
                                         store=True)

    def cancel_product(self):
        self.env['material.request.product.final'].search([]).unlink()
        return {'type': 'ir.actions.act_window_close'}

    @api.onchange('search_pd','search_pd2', 'category_id')
    def search_char(self):
        # self.env['purchase.product.first'].search([]).unlink()
        self.product_ids = False
        products = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
        products_with_pd = self.env['product.product'].search(
            ['|',('name', 'ilike', self.search_pd),('default_code', 'ilike', self.search_pd2)])
        data = []
        if self.category_id and not self.search_pd and not self.search_pd2:
            for prod in products:
                line = self.env['material.request.product.first'].create({
                    'product_id': prod.id})
                data.append(line.id)
            self.product_ids = data
        if self.category_id and (self.search_pd or self.search_pd2):
            print('aaaaaaaaaaaaaaaaaaaaaaaaa')
            for prod in products_with_pd:
                print('sssssssssssssssss')
                if prod.categ_id.id == self.category_id.id:
                    line = self.env['material.request.product.first'].create({
                        'product_id': prod.id})
                    data.append(line.id)
            self.product_ids = data

        if not self.category_id and (self.search_pd or self.search_pd2):
            print ('kkkkkkkkkk')
            for prod in self.env['product.product'].search(
            ['|', ('name', 'ilike', self.search_pd), ('default_code', 'ilike', self.search_pd2)]):
                print('sssssssssssssssss')
                # if prod.categ_id.id == self.category_id.id:
                line = self.env['material.request.product.first'].create({
                    'product_id': prod.id})
                data.append(line.id)
            self.product_ids = data



    @api.onchange('product_ids')
    def search_product(self):
        data = [line.id for line in self.env['material.request.product.final'].search([])]
        products = [line.product_id.id for line in self.env['material.request.product.final'].search([])]
        for line in self.product_ids.filtered(lambda c: c.choose and c.quantity):
            if line.product_id.id not in products:
                final_line = self.env['material.request.product.final'].create({
                    'product_id': line.product_id.id,
                    # 'module_id': line.module_id.id,
                    'quantity': line.quantity,
                })
                data.append(final_line.id)
            else:
                for product in self.final_product_ids:
                    if product.product_id.id == line.product_id.id:
                        product.update({
                            'product_id': line.product_id.id,
                            # 'module_id': line.module_id.id,
                            'quantity': line.quantity,
                        })
                        break
        self.final_product_ids = data
        return {'type': 'ir.actions.act_window_open'}

    def get_final_product(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            run_data = self.env['request.delivery'].browse(active_id)
        if not self.env['material.request.product.final'].search([]):
            raise UserError(_("You must add product(s) to generate Material Request(s)."))
        for product in self.env['material.request.product.final'].search([]):
            res = {
                'request_delivery_id': active_id,
                'product_id': product.product_id.id,
                'product_uom_id': product.product_id.uom_id.id,
                # 'modules_name_id': product.module_id.id,
                # 'name': product.product_id.name,
                'product_qty': product.quantity,
            }
            run_data.write({'pack_operation_product_ids': [(0, 0, res)]})
        self.env['material.request.product.final'].search([]).unlink()
        return {'type': 'ir.actions.act_window_close'}


class SaleProductFirst(models.Model):
    _name = 'sale.product.first'
    _rec_name = 'product_id'

    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=False, store=True)
    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )
    # module_id = fields.Many2one(comodel_name="sales.model.name", string="Model", required=False, )
    quantity = fields.Float(string="Quantity", required=False, )
    price_unit = fields.Float(string="price_unit", required=False,  )  #compute='get_price_from_supplier'
    choose = fields.Boolean(string="Choose", )
    # discount = fields.Float(string="Discount", required=False, compute='get_discount')

    # @api.multi
    # @api.onchange('module_id', 'choose')
    # def filter_modules_name2(self):
    #     if self.product_id:
    #         res = self.env['product.template'].search([('id', '=', self.product_id.product_tmpl_id.id)])
    #         modules_list = []
    #         for line in res:
    #             for rec in line.modules_name_id:
    #                 modules_list.append(rec.id)
    #
    #         return {
    #             'domain': {
    #                 'module_id': [('id', 'in', modules_list)]
    #             }
    #         }

    # @api.one
    # @api.depends('product_id', 'discount')
    # def get_discount(self):
    #     self.ensure_one()
    #     records = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
    #     for rec in records:
    #         if rec.is_discount_categ == True:
    #             # print('3aaaaaaaash')
    #             for categ in rec.categ_discount_ids:
    #                 # print('cateeeeeeg')
    #                 if self.product_id.categ_id.id == categ.categ_id.id:
    #                     # print('tmaaaam')
    #                     self.update({'discount': categ.discount})
    #                 elif self.product_id.categ_id.id != categ.categ_id.id:
    #                     self.update({'discount': rec.available_discount})

    # @api.multi
    # @api.onchange('product_id')
    # def get_price_from_supplier(self):
    #     for line in self:
    #         partner = line.partner_id if not line.partner_id.parent_id else line.partner_id.parent_id
    #         for rec in line.product_id.seller_ids:
    #             if partner in rec.mapped('name'):
    #                 line.price_unit = rec.price


class SaleProductFinal(models.Model):
    _name = 'sale.product.final'
    _rec_name = 'product_id'

    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )
    module_id = fields.Many2one(comodel_name="sales.model.name", string="Model", required=False, )
    quantity = fields.Float(string="Quantity", required=False, )
    # discount = fields.Float(string="Discount", required=False, )
    price_unit = fields.Float(string="price_unit", required=False, )

    # @api.one
    # @api.depends('product_id')
    # def get_discount(self):
    #     self.ensure_one()
    #     records = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
    #     for rec in records:
    #         if rec.is_discount_categ == True:
    #             # print('3aaaaaaaash')
    #             for categ in rec.categ_discount_ids:
    #                 # print('cateeeeeeg')
    #                 if self.product_id.categ_id.id == categ.categ_id.id:
    #                     # print('tmaaaam')
    #                     self.update({'discount': categ.discount})
    #                 elif self.product_id.categ_id.id != categ.categ_id.id:
    #                     self.update({'discount': rec.available_discount})




class PurchaseProductFirst(models.Model):
    _name = 'purchase.product.first'
    _rec_name = 'product_id'


    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=False, )
    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )
    # module_id = fields.Many2one(comodel_name="sales.model.name", string="Model", required=False, )
    quantity = fields.Float(string="Quantity", required=False, )
    price_unit = fields.Float(string="Unit Price", required=False,compute='get_price_from_supplier' )
    choose = fields.Boolean(string="Choose", )

    @api.multi
    @api.onchange('product_id')
    def get_price_from_supplier(self):
        for line in self:
            partner = line.partner_id if not line.partner_id.parent_id else line.partner_id.parent_id
            for rec in line.product_id.seller_ids:
                if partner in rec.mapped('name'):
                    line.price_unit = rec.price

    # discount = fields.Float(string="Discount",  required=False, )

    # @api.multi
    # @api.onchange('module_id', 'choose')
    # def filter_modules_name(self):
    #     if self.product_id:
    #         res = self.env['product.template'].search([('id', '=', self.product_id.product_tmpl_id.id)])
    #         modules_list = []
    #         for line in res:
    #             for rec in line.modules_name_id:
    #                 modules_list.append(rec.id)
    #
    #         return {
    #             'domain': {
    #                 'module_id': [('id', 'in', modules_list)]
    #             }
    #         }


class PurchaseProductFinal(models.Model):
    _name = 'purchase.product.final'
    _rec_name = 'product_id'

    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )
    module_id = fields.Many2one(comodel_name="sales.model.name", string="Model", required=False, )
    quantity = fields.Float(string="Quantity", required=False, )
    price_unit = fields.Float(string="Price Unit",  required=False, )


# class PurchaseRequestProductFirst(models.Model):
#     _name = 'purchase.request.product.first'
#     _rec_name = 'product_id'
#
#     partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=False, )
#     product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )
#     module_id = fields.Many2one(comodel_name="sales.model.name", string="Model", required=False, )
#     quantity = fields.Float(string="Quantity", required=False, )
#     choose = fields.Boolean(string="Choose", )
#
#     # discount = fields.Float(string="Discount",  required=False, )
#
#     @api.multi
#     @api.onchange('module_id', 'choose')
#     def filter_modules_name1(self):
#         if self.product_id:
#             res = self.env['product.template'].search([('id', '=', self.product_id.product_tmpl_id.id)])
#             modules_list = []
#             for line in res:
#                 for rec in line.modules_name_id:
#                     modules_list.append(rec.id)
#
#             return {
#                 'domain': {
#                     'module_id': [('id', 'in', modules_list)]
#                 }
#             }
#
#
# class PurchaseProductFinal(models.Model):
#     _name = 'purchase.request.product.final'
#     _rec_name = 'product_id'
#
#     product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )
#     module_id = fields.Many2one(comodel_name="sales.model.name", string="Model", required=False, )
#     quantity = fields.Float(string="Quantity", required=False, )
#     # discount = fields.Float(string="Discount",  required=False, )
#
#
class PurchaseMaterialRequestProductFirst(models.Model):
    _name = 'material.request.product.first'
    _rec_name = 'product_id'

    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=False, )
    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )
    # module_id = fields.Many2one(comodel_name="sales.model.name", string="Model", required=False, )
    quantity = fields.Float(string="Quantity", required=False, )
    choose = fields.Boolean(string="Choose", )

    # discount = fields.Float(string="Discount",  required=False, )

    # @api.multi
    # @api.onchange('module_id', 'choose')
    # def filter_modules_name1(self):
    #     if self.product_id:
    #         res = self.env['product.template'].search([('id', '=', self.product_id.product_tmpl_id.id)])
    #         modules_list = []
    #         for line in res:
    #             for rec in line.modules_name_id:
    #                 modules_list.append(rec.id)
    #
    #         return {
    #             'domain': {
    #                 'module_id': [('id', 'in', modules_list)]
    #             }
    #         }


class PurchaseMaterialProductFinal(models.Model):
    _name = 'material.request.product.final'
    _rec_name = 'product_id'

    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )
    # module_id = fields.Many2one(comodel_name="sales.model.name", string="Model", required=False, )
    quantity = fields.Float(string="Quantity", required=False, )
    # discount = fields.Float(string="Discount",  required=False, )
