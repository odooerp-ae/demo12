# -*- coding: utf-8 -*-
from odoo import http

# class InvoiceMargin(http.Controller):
#     @http.route('/invoice_margin/invoice_margin/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_margin/invoice_margin/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_margin.listing', {
#             'root': '/invoice_margin/invoice_margin',
#             'objects': http.request.env['invoice_margin.invoice_margin'].search([]),
#         })

#     @http.route('/invoice_margin/invoice_margin/objects/<model("invoice_margin.invoice_margin"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_margin.object', {
#             'object': obj
#         })