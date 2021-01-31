# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class Partner(models.Model):
    _inherit = "res.partner"

    status = fields.Selection([('draft', 'Draft'), ('approved', 'Approved')], string="State")
    country_group_id = fields.Many2one(comodel_name='res.country.group', string="Region", required=True)
    help_disck_count = fields.Integer(compute='_compute_help_disck_count', string='# of HelpDesk Tickets')
    email = fields.Char(required=True)
    mobile = fields.Char(required=True)
    facebook = fields.Char()
    twitter = fields.Char()
    linkedin = fields.Char()
    instgram = fields.Char()
    fax = fields.Char()
    is_company = fields.Boolean(default=True)
    brand_ids = fields.Many2many(comodel_name='product.attribute.value',domain=[('is_brand','=',True)], string="Brands")
    city = fields.Char(required=True)
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', required=True)
    user_type = fields.Selection([('private', 'Private'), ('distributer', 'Distributer'), ('user', 'End User')],
                                 string="Customer Type")

    @api.multi
    def _compute_help_disck_count(self):
        for record in self:
            # helpdesk_count = self.env['helpdesk.ticket'].sudo().search_count([('partner_id', '=', record.id)])
            # record.help_disck_count = helpdesk_count
            record.help_disck_count =0

    @api.multi
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if self.sudo().search([('id', '!=', record.id), ('name', '!=', "")]).filtered(
                    lambda p: p.name == record.name):
                created_uid=self.sudo().search([('id', '!=', record.id), ('name', '!=', "")]).filtered(
                    lambda p: p.name == record.name).create_uid.name
                raise ValidationError("Customer Name Should be Unique. \n "
                                      "This customer might be an existing customer with our company, and created by %s"
                                      "  ,kindly check with the management" % (created_uid))

    @api.multi
    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if self.sudo().search([('id', '!=', record.id), ('email', '!=', "")]).filtered(
                    lambda p: p.email == record.email) or self.env['crm.lead'].sudo().search(
                [('email_from', '!=', ""), ('partner_id', '=',False),('partner_name','=',False)]).filtered(
                lambda p: p.email_from == record.email):

                if  self.sudo().search([('id', '!=', record.id), ('email', '!=', "")]).filtered(
                    lambda p: p.email == record.email):
                    created_uid = self.sudo().search([('id', '!=', record.id), ('email', '!=', "")]).filtered(
                    lambda p: p.email == record.email)[0].create_uid.name
                    partner_name= self.sudo().search([('id', '!=', record.id), ('email', '!=', "")]).filtered(
                    lambda p: p.email == record.email)[0].name

                    raise ValidationError(
                        "This Customer might be an existing Customer in our company, Customer Name : %s \n "
                        " ,created by %s has the same Email "
                        "  ,kindly check with the management" % (partner_name, created_uid))

                elif  self.env['crm.lead'].sudo().search(
                         [('email_from', '!=', ""), ('partner_id', '=',False),('partner_name','=',False)]).filtered(
                        lambda p: p.email_from == record.email):
                    created_uid =  self.env['crm.lead'].sudo().search(
                         [('email_from', '!=', ""), ('partner_id', '=',False),('partner_name','=',False)]).filtered(
                        lambda p: p.email_from == record.email)[0].create_uid.name

                    raise ValidationError("This Customer might be an existing Customer in our company \n "
                                          " ,created by %s has the same Email "
                                          "  ,kindly check with the management" % (created_uid))



    # @api.multi
    # @api.constrains('mobile')
    # def _check_mobile(self):
    #     for record in self:
    #         if self.sudo().search([('id', '!=', record.id), ('mobile', '!=', "")]).filtered(
    #                 lambda p: p.mobile == record.mobile) or self.env['crm.lead'].sudo().search(
    #             [('mobile', '!=', ""),('partner_id', '=',False),('partner_name','=',False)]).filtered(
    #             lambda p: p.mobile == record.mobile):
    #             if self.sudo().search([('id', '!=', record.id), ('mobile', '!=', "")]).filtered(
    #                     lambda p: p.mobile == record.mobile):
    #                 created_uid = self.sudo().search([('id', '!=', record.id), ('mobile', '!=', "")]).filtered(
    #                     lambda p: p.mobile == record.mobile)[0].create_uid.name
    #                 partner_name = self.sudo().search([('id', '!=', record.id), ('mobile', '!=', "")]).filtered(
    #                     lambda p: p.mobile == record.mobile)[0].name
    #
    #                 raise ValidationError(
    #                     "This Customer might be an existing Customer in our company, Customer Name : %s \n "
    #                     " ,created by %s has the same mobile"
    #                     "  ,kindly check with the management" % (partner_name, created_uid))
    #
    #             elif self.env['crm.lead'].sudo().search(
    #                     [('mobile', '!=', ""), ('partner_id', '=', False), ('partner_name', '=', False)]).filtered(
    #                 lambda p: p.mobile == record.mobile):
    #                 created_uid = self.env['crm.lead'].sudo().search(
    #                     [('mobile', '!=', ""), ('partner_id', '=', False), ('partner_name', '=', False)]).filtered(
    #                     lambda p: p.mobile == record.mobile)[0].create_uid.name
    #
    #                 raise ValidationError("This Customer might be an existing Customer in our company \n "
    #                                       " ,created by %s has the same mobile "
    #                                       "  ,kindly check with the management" % (created_uid))
    _sql_constraints = [
        ('unique_name','UNIQUE(mobile)','Mobile Must Be unique! ')
    ]
    @api.multi
    @api.constrains('facebook')
    def _check_facebook(self):
        for record in self:
            if self.sudo().search([('id', '!=', record.id), ('facebook', '!=', "")]).filtered(
                    lambda p: p.facebook == record.facebook) or self.env['crm.lead'].sudo().search(
                [('facebook', '!=', ""),('partner_id', '=',False),('partner_name','=',False)]).filtered(
                lambda p: p.facebook == record.facebook):
                if self.sudo().search([('id', '!=', record.id), ('facebook', '!=', "")]).filtered(
                        lambda p: p.facebook == record.facebook):
                    created_uid = self.sudo().search([('id', '!=', record.id), ('facebook', '!=', "")]).filtered(
                        lambda p: p.facebook == record.facebook)[0].create_uid.name
                    partner_name = self.sudo().search([('id', '!=', record.id), ('facebook', '!=', "")]).filtered(
                        lambda p: p.facebook == record.facebook)[0].name

                    raise ValidationError(
                        "This Customer might be an existing Customer in our company, Customer Name : %s \n "
                        " ,created by %s has the same facebook "
                        "  ,kindly check with the management" % (partner_name, created_uid))

                elif self.env['crm.lead'].sudo().search(
                        [('facebook', '!=', ""), ('partner_id', '=', False), ('partner_name', '=', False)]).filtered(
                    lambda p: p.facebook == record.facebook):
                    created_uid = self.env['crm.lead'].sudo().search(
                        [('facebook', '!=', ""), ('partner_id', '=', False), ('partner_name', '=', False)]).filtered(
                        lambda p: p.facebook == record.facebook)[0].create_uid.name

                    raise ValidationError("This Customer might be an existing Customer in our company \n "
                                          " ,created by %s has the same facebook "
                                          "  ,kindly check with the management" % (created_uid))

    @api.multi
    @api.constrains('twitter')
    def _check_twitter(self):
        for record in self:
            if self.sudo().search([('id', '!=', record.id), ('twitter', '!=', "")]).filtered(
                    lambda p: p.twitter == record.twitter) or self.env['crm.lead'].sudo().search(
                [('twitter', '!=', ""),('partner_id', '=',False),('partner_name','=',False)]).filtered(
                lambda p: p.twitter == record.twitter):
                if self.sudo().search([('id', '!=', record.id), ('twitter', '!=', "")]).filtered(
                        lambda p: p.twitter == record.twitter):
                    created_uid = self.sudo().search([('id', '!=', record.id), ('twitter', '!=', "")]).filtered(
                        lambda p: p.twitter == record.twitter)[0].create_uid.name
                    partner_name = self.sudo().search([('id', '!=', record.id), ('twitter', '!=', "")]).filtered(
                        lambda p: p.twitter == record.twitter)[0].name

                    raise ValidationError(
                        "This Customer might be an existing Customer in our company, Customer Name : %s \n "
                        " ,created by %s has the same twitter"
                        "  ,kindly check with the management" % (partner_name, created_uid))

                elif self.env['crm.lead'].sudo().search(
                        [('twitter', '!=', ""), ('partner_id', '=', False), ('partner_name', '=', False)]).filtered(
                    lambda p: p.twitter == record.twitter):
                    created_uid = self.env['crm.lead'].sudo().search(
                        [('twitter', '!=', ""), ('partner_id', '=', False), ('partner_name', '=', False)]).filtered(
                        lambda p: p.twitter == record.twitter)[0].create_uid.name

                    raise ValidationError("This Customer might be an existing Customer in our company \n "
                                          " ,created by %s has the same twitter "
                                          "  ,kindly check with the management" % (created_uid))

    @api.multi
    @api.constrains('linkedin')
    def _check_linkedin(self):
        for record in self:
            if self.sudo().search([('id', '!=', record.id), ('linkedin', '!=', "")]).filtered(
                    lambda p: p.linkedin == record.linkedin) or self.env['crm.lead'].sudo().search(
                [('linkedin', '!=', ""),('partner_id', '=',False),('partner_name','=',False)]).filtered(
                lambda p: p.linkedin == record.linkedin):
                if self.sudo().search([('id', '!=', record.id), ('linkedin', '!=', "")]).filtered(
                        lambda p: p.linkedin == record.linkedin):
                    created_uid = self.sudo().search([('id', '!=', record.id), ('linkedin', '!=', "")]).filtered(
                        lambda p: p.linkedin == record.linkedin)[0].create_uid.name
                    partner_name = self.sudo().search([('id', '!=', record.id), ('linkedin', '!=', "")]).filtered(
                        lambda p: p.linkedin == record.linkedin)[0].name

                    raise ValidationError(
                        "This Customer might be an existing Customer in our company, Customer Name : %s \n "
                        " ,created by %s has the same linkedin "
                        "  ,kindly check with the management" % (partner_name, created_uid))

                elif self.env['crm.lead'].sudo().search(
                        [('linkedin', '!=', ""), ('partner_id', '=', False), ('partner_name', '=', False)]).filtered(
                    lambda p: p.linkedin == record.linkedin):
                    created_uid = self.env['crm.lead'].sudo().search(
                        [('linkedin', '!=', ""), ('partner_id', '=', False), ('partner_name', '=', False)]).filtered(
                        lambda p: p.linkedin == record.linkedin)[0].create_uid.name

                    raise ValidationError("This Customer might be an existing Customer in our company \n "
                                          " ,created by %s has the same linkedin "
                                          "  ,kindly check with the management" % (created_uid))

    @api.multi
    @api.constrains('instgram')
    def _check_instgram(self):
        for record in self:
            if self.sudo().search([('id', '!=', record.id), ('instgram', '!=', "")]).filtered(
                    lambda p: p.instgram == record.instgram) or self.env['crm.lead'].sudo().search(
                [('instgram', '!=', ""),('partner_id', '=',False),('partner_name','=',False)]).filtered(
                lambda p: p.instgram == record.instgram):
                if  self.sudo().search([('id', '!=', record.id), ('instgram', '!=', "")]).filtered(
                    lambda p: p.instgram == record.instgram):
                    created_uid = self.sudo().search([('id', '!=', record.id), ('instgram', '!=', "")]).filtered(
                    lambda p: p.instgram == record.instgram)[0].create_uid.name
                    partner_name= self.sudo().search([('id', '!=', record.id), ('instgram', '!=', "")]).filtered(
                    lambda p: p.instgram == record.instgram)[0].name

                    raise ValidationError(
                        "This Customer might be an existing Customer in our company, Customer Name : %s \n "
                        " ,created by %s has the same instgram "
                        "  ,kindly check with the management" % (partner_name, created_uid))

                elif  self.env['crm.lead'].sudo().search(
                         [('instgram', '!=', ""), ('partner_id', '=',False),('partner_name','=',False)]).filtered(
                        lambda p: p.instgram == record.instgram):
                    created_uid =  self.env['crm.lead'].sudo().search(
                         [('instgram', '!=', ""), ('partner_id', '=',False),('partner_name','=',False)]).filtered(
                        lambda p: p.instgram == record.instgram)[0].create_uid.name

                    raise ValidationError("This Customer might be an existing Customer in our company \n "
                                          " ,created by %s has the same instgram "
                                          "  ,kindly check with the management" % (created_uid))


    @api.multi
    @api.constrains('website')
    def _check_website(self):
        for record in self:
            if self.sudo().search([('id', '!=', record.id), ('website', '!=', "")]).filtered(
                    lambda p: p.website == record.website) or self.env['crm.lead'].sudo().search(
                [('website', '!=', ""),('partner_id', '=',False),('partner_name','=',False)],).filtered(
                lambda p: p.website == record.website):
                if  self.sudo().search([('id', '!=', record.id), ('website', '!=', "")]).filtered(
                    lambda p: p.website == record.website):
                    created_uid = self.sudo().search([('id', '!=', record.id), ('website', '!=', "")]).filtered(
                    lambda p: p.website == record.website)[0].create_uid.name
                    partner_name= self.sudo().search([('id', '!=', record.id), ('website', '!=', "")]).filtered(
                    lambda p: p.website == record.website)[0].name

                    raise ValidationError(
                        "This Customer might be an existing Customer in our company, Customer Name : %s \n "
                        " ,created by %s has the same website"
                        "  ,kindly check with the management" % (partner_name, created_uid))

                elif  self.env['crm.lead'].sudo().search(
                         [('website', '!=', ""), ('partner_id', '=',False),('partner_name','=',False)]).filtered(
                        lambda p: p.website == record.website):
                    created_uid =  self.env['crm.lead'].sudo().search(
                         [('website', '!=', ""), ('partner_id', '=',False),('partner_name','=',False)]).filtered(
                        lambda p: p.website == record.website)[0].create_uid.name

                    raise ValidationError("This Customer might be an existing Customer in our company \n "
                                          " ,created by %s has the same website "
                                          "  ,kindly check with the management" % (created_uid))


    @api.multi
    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if self.sudo().search([('id', '!=', record.id), ('phone', '!=', "")]).filtered(
                    lambda p: p.phone == record.phone) or self.env['crm.lead'].sudo().search(
                [('phone', '!=', ""),('partner_id', '=',False),('partner_name','=',False)]).filtered(
                lambda p: p.phone == record.phone):
                if self.sudo().search([('id', '!=', record.id), ('phone', '!=', "")]).filtered(
                        lambda p: p.phone == record.phone):
                    created_uid = self.sudo().search([('id', '!=', record.id), ('phone', '!=', "")]).filtered(
                        lambda p: p.phone == record.phone)[0].create_uid.name
                    partner_name = self.sudo().search([('id', '!=', record.id), ('phone', '!=', "")]).filtered(
                        lambda p: p.phone == record.phone)[0].name

                    raise ValidationError(
                        "This Customer might be an existing Customer in our company, Customer Name : %s \n "
                        " ,created by %s has the same phone "
                        "  ,kindly check with the management" % (partner_name, created_uid))

                elif self.env['crm.lead'].sudo().search(
                        [('phone', '!=', ""), ('partner_id', '=', False), ('partner_name', '=', False)]).filtered(
                    lambda p: p.phone == record.phone):
                    created_uid = self.env['crm.lead'].sudo().search(
                        [('phone', '!=', ""), ('partner_id', '=', False), ('partner_name', '=', False)]).filtered(
                        lambda p: p.phone == record.phone)[0].create_uid.name

                    raise ValidationError("This Customer might be an existing Customer in our company \n "
                                          " ,created by %s has the same phone "
                                          "  ,kindly check with the management" % (created_uid))

    @api.one
    def set_approved(self):
        self.status = 'approved'

    @api.model
    def create(self, vals):
        if vals.get('child_ids') == []:
            raise UserError(_("Couldn't create customer without any contact!"))
        partner = super(Partner, self).create(vals)

        partner.status = 'draft'
        return partner


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        super(SaleOrder, self).action_confirm()
        for order in self:
            if order.partner_id.status == 'draft':
                raise UserError(_("Customer must be approved."))
        return True
