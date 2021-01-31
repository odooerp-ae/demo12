# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shipment_type = fields.Selection([('Road', 'By Road'), ('Sea', 'By Sea')],
                                     string='Shipment Type')
    coc = fields.Selection([('no', 'Not Applicable -N/A'), ('yes', 'Required')],
                           string='Certificate of Analysis - COA')
    coo = fields.Selection([('na', 'Not Applicable -N/A'), ('coc', 'Chamber of Commerce'),
                            ('moe', 'Ministry of economy'),
                            ('mecc','Ministry of economy & Chamber of commerce')],
                           string='Certificate of Origin -COO')
    embassy_attestation = fields.Selection(
        [('no', 'Not Applicable -N/A'), ('yes', 'Required Paid By Us'),
         ('yes', 'Required Paid By Customer Separatly')],
        string='Embassy Attestation')

    #port = fields.Char(string="Port")
    port_id = fields.Many2one('res.port',string="Port")

    incoterm = fields.Many2one(
        'account.incoterms',
        'Incoterms',
        help="International Commercial Terms are a series of predefined commercial terms used "
             "in international transactions.",
    )
    co_conformity = fields.Selection([('no', 'Not Applicable -N/A'), ('yes', 'Required Paid By Us'),
                                      ('yes', 'Required Paid By Customer Separatly')],
                                     string='Certificate of Conformity -COC')
    msds = fields.Selection([('no', 'Not Applicable -N/A'), ('yes', 'Required')],
                           string='MSDS')

    @api.onchange('incoterm')
    def _onchange_incoterms(self):
        if self.incoterm.id == 4:
            return {'domain': {'port_id': [('id', 'in', self.env['res.port'].sudo().search([('country_id','=',2)]).mapped('id'))]}}
        else:
            return {'domain': {
                'port_id': [('id', 'in', self.env['res.port'].sudo().search([]).mapped('id'))]}}


    @api.multi
    def _action_confirm(self):
        for order in self:
            if not order.coc:
                raise UserError(_('Certificate of Analysis- COA required.'))
            if not order.coo:
                raise UserError(_('Certificate of Origin -COO  required.'))
            if not order.embassy_attestation:
                raise UserError(_('Embassy Attestation required.'))
            if not order.incoterm:
                raise UserError(_('Incoterms required.'))
            if not order.co_conformity:
                raise UserError(_('Certificate of Conformity -COC required.'))
            if order.incoterm.id != 1 and not order.shipment_type:
                raise UserError(_('Shipment Type required.'))
            if not order.msds:
                raise UserError(_('MSDS required.'))

        return super(SaleOrder, self)._action_confirm()


class ResCountryGroup(models.Model):
    _inherit = 'res.country.group'

    fiscal_position_id=fields.Many2one('account.fiscal.position',string='Fiscal Position')

class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_position_id=fields.Many2one('account.fiscal.position',related='country_group_id.fiscal_position_id', string='Fiscal Position')

    #fiscal_position_id_related = fields.Many2one('account.fiscal.position',related='country_group_id.fiscal_position_id', string='Fiscal Position')

class ResPort(models.Model):
    _name='res.port'

    name=fields.Char()
    country_id=fields.Many2one('res.country')
    default_code=fields.Char('Code',index=True)

    @api.model
    def create(self,vals):
        res=super(ResPort,self).create(vals)
        res.name ='['+res.default_code+'] '+res.name
        return res
