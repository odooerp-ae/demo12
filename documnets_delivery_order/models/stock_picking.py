# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.depends('origin', 'picking_type_code')
    def _get_vendor_ref(self):
        for record in self:
            if record.origin and record.picking_type_code == 'incoming':
                partner_ref = self.env['purchase.order'].search(
                    [('name', '=', record.origin)],
                    limit=1,
                ).mapped('partner_ref')
                if partner_ref:
                    record.partner_reef = partner_ref[0]

    partner_reef = fields.Char(compute='_get_vendor_ref', string='Vendor Reference')

    @api.depends('origin')
    def _get_order_data(self):
        for stock in self:
            if stock.origin:
                sale_order = self.env['sale.order'].search([('name', '=', stock.origin)], limit=1)
                stock.incoterm_sale = sale_order.incoterm.code
                stock.coc = sale_order.co_conformity
                stock.embassy_attestation = sale_order.embassy_attestation
                stock.customer_country = sale_order.partner_id.country_id.name
                stock.msds = sale_order.msds

    state = fields.Selection(selection_add=[('documented', 'Documented')])
    '''
    bol_doc_ids = fields.One2many('bol.attachments', 'stock_bol_id', string='Bill of Lading')
    pl_doc_ids = fields.One2many('pl.attachments', 'stock_pl_id', string='Picking List', required=True)
    ci_doc_ids = fields.One2many('ci.attachments', 'stock_ci_id', string='Commercial Invoice', required=True)
    coa_doc_ids = fields.One2many('coa.attachments', 'stock_coa_id', string='Certificate of Analysis', required=True)
    coc_doc_ids = fields.One2many('coc.attachments', 'stock_coc_id', string='Certificate of Confirmation')

    coo_doc_ids = fields.One2many('coo.attachments', 'stock_coo_id', string='Certificate of Origin')
    ea_doc_ids = fields.One2many('ea.attachments', 'stock_ea_id', string='Embassy Attestation')
    ip_doc_ids = fields.One2many('ip.attachments', 'stock_ip_id', string='Insurance Policy')

    clp_doc_ids = fields.One2many('clp.attachments', 'stock_clp_id', string='Container Loading Protocol', required=True)
    vr_doc_ids = fields.One2many('vr.attachments', 'stock_vr_id', string='Vehicle Registration', required=True)
    di_doc_ids = fields.One2many('di.attachments', 'stock_di_id', string='Driver ID', required=True)
    '''

    @api.one
    def _required_coo(self):
        if self.origin:
            if self.env['sale.order'].search([('name', '=', self.origin)], limit=1).coo != 'na':
                return False
            else:
                return True

    bol_doc = fields.Binary(string='Bill of Lading -BL')
    pl_doc = fields.Binary(string='Picking List')
    ci_doc = fields.Binary(string='Commercial Invoice')
    coa_doc = fields.Binary(string='Certificate of Analysis')
    coc_doc = fields.Binary(string='Certificate of Confirmaty')

    coo_doc = fields.Binary(string='Certificate of Origin')
    ea_doc = fields.Binary(string='Embassy Attestation')
    ip_doc = fields.Binary(string='Insurance Policy')

    clp_doc = fields.Binary(string='Container Loading Protocol-CLP')
    vr_doc = fields.Binary(string='Vehicle Registration')
    di_doc = fields.Binary(string='Driver ID')

    incoterm_sale = fields.Char(compute=_get_order_data)
    coc = fields.Char(compute=_get_order_data)
    embassy_attestation = fields.Char(compute=_get_order_data)
    customer_country = fields.Char(compute=_get_order_data)
    coo_sale = fields.Boolean(compute='_compute_coo_sale')
    msds_doc = fields.Binary(string='MSDS')
    msds = fields.Char(compute=_get_order_data)

    @api.multi
    @api.depends('origin')
    def _compute_coo_sale(self):
        for stock in self:
            sale_order = self.env['sale.order'].search([('name', '=', stock.origin)], limit=1)
            stock.coo_sale = True if sale_order and (
                    sale_order.coo == 'coc' or sale_order.coo == 'moe'
            ) else False

    @api.multi
    def action_documented(self):
        # if self.incoterm_sale != 'EXW' and not self.bol_doc:
        if self.incoterm_sale in ["CFR", "CIF"] and not self.bol_doc:
            raise UserError(_('You Must upload bill of lading document.'))
        # if not self.pl_doc:
        #     raise UserError(_('You Must upload picking list document.'))
        # if not self.ci_doc:
        #     raise UserError(_('You Must upload Commercial Invoice document.'))
        # if not self.coa_doc:
        #     raise UserError(_('You Must upload Certificate of Analysis document.'))
        # if not self.clp_doc:
        #     raise UserError(_('You Must upload Container Loading Protocol document.'))
        # if not self.vr_doc:
        #     raise UserError(_('You Must upload Vehicle Registration document.'))
        # if not self.di_doc:
        #     raise UserError(_('You Must upload Driver ID document.'))
        if self.coc == 'yes' and not self.coc_doc:
            raise UserError(_('You Must upload Certificate of Confirmaty document.'))
        if self.incoterm_sale != 'EXW' and not self.di_doc:
            raise UserError(_('You Must upload Insurance Policy document.'))
        if self.coo_sale and not self.coo_doc:
            raise UserError(_('You Must upload Certificate of Origin document.'))
        if self.embassy_attestation == 'yes' and not self.ea_doc:
            raise UserError(_('You Must upload Embassy Attestation document.'))

        if self.incoterm_sale == 'CIF' and not self.ip_doc:
            raise UserError(_('You Must upload Insurance Policy document.'))
        if self.msds == 'yes' and not self.msds_doc:
            raise UserError(_('You Must upload MSDS document.'))

        self.write({'state': 'documented'})
        return True


'''
class CooAttachments(models.Model):
    _name = 'coo.attachments'

    name = fields.Binary()
    stock_coo_id = fields.Many2one('stock.picking')


class EaAttachments(models.Model):
    _name = 'ea.attachments'

    name = fields.Binary()
    stock_ea_id = fields.Many2one('stock.picking')


class IpAttachments(models.Model):
    _name = 'ip.attachments'

    name = fields.Binary()
    stock_ip_id = fields.Many2one('stock.picking')


class BolAttachments(models.Model):
    _name = 'bol.attachments'

    name = fields.Binary()
    stock_bol_id = fields.Many2one('stock.picking')


class PlAttachments(models.Model):
    _name = 'pl.attachments'

    name = fields.Binary()
    stock_pl_id = fields.Many2one('stock.picking')


class CiAttachments(models.Model):
    _name = 'ci.attachments'

    name = fields.Binary()
    stock_ci_id = fields.Many2one('stock.picking')


class CoaAttachments(models.Model):
    _name = 'coa.attachments'

    name = fields.Binary()
    stock_coa_id = fields.Many2one('stock.picking')


class CocAttachments(models.Model):
    _name = 'coc.attachments'

    name = fields.Binary()
    stock_coc_id = fields.Many2one('stock.picking')


class ClpAttachments(models.Model):
    _name = 'clp.attachments'

    name = fields.Binary()
    stock_clp_id = fields.Many2one('stock.picking')


class VrAttachments(models.Model):
    _name = 'vr.attachments'

    name = fields.Binary()
    stock_vr_id = fields.Many2one('stock.picking')


class DiAttachments(models.Model):
    _name = 'di.attachments'

    name = fields.Binary()
    stock_di_id = fields.Many2one('stock.picking')
'''
