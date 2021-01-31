# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
import logging
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError,ValidationError

from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import date_utils

class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    is_brand=fields.Boolean('Is Brand')

class Lead(models.Model):
    _inherit = "crm.lead"

    container = fields.Integer(string="Container")
    margin = fields.Float(string="Margin", compute='_compute_margin', digits=(16, 2))
    margin_aed_container = fields.Float(string="Margin Per Container", compute='_compute_margin_aed_container')
    margin_value = fields.Float(string="Margin Value")
    brand_ids = fields.Many2many(comodel_name='product.attribute.value',domain=[('is_brand','=',True)], string="Brands")
    country_group_id = fields.Many2one(comodel_name='res.country.group', string="Region", required=True)
    user_type = fields.Selection([('private', 'Private'), ('distributer', 'Distributer'), ('user', 'End User')],
                                 string="Customer Type")
    email_from = fields.Char('Email', help="Email address of the contact", index=True)
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', change_default=True)
    city = fields.Char('City', required=True)
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country', required=True)
    phone = fields.Char('Phone')
    fax = fields.Char('Fax')
    mobile = fields.Char('Mobile')
    facebook = fields.Char()
    twitter = fields.Char()
    linkedin = fields.Char()
    instgram = fields.Char()
    currency_id=fields.Many2one('res.currency',string='Currency')
    converted_amount=fields.Float(string='Total Amount Currency')
    planned_revenue = fields.Monetary(compute='_get_converted_amount',store=True, currency_field='company_currency', track_visibility='always')
    planned_revenue_kanban = fields.Monetary(compute='_get_converted_amount',store=True, currency_field='company_currency', track_visibility='always')

    contact_mobile = fields.Char('Contact Mobile')

    @api.multi
    @api.depends('converted_amount')
    def _get_converted_amount(self):
        for lead in self:
            currency = lead.currency_id
            if currency.rate != 0:
                lead.planned_revenue = lead.converted_amount / currency.rate
                lead.planned_revenue_kanban=lead.planned_revenue


    @api.model
    def create(self,vals):
        if 'country_id' in vals and 'brand_ids' in vals:
            country_id=vals.get('country_id')
            brand_ids=vals.get('brand_ids')[0][2]
            partner_id = vals.get('partner_id')
            exist=False
            leads=self.search([('country_id','=',country_id),('brand_ids','in',brand_ids)])
            if leads:
                for lead in leads:
                    if lead.partner_id.id == partner_id:
                       exist=True
                if not exist or partner_id == False:
                   raise ValidationError("Restricted,this opportunity with this brand and this country already exist")

        return super(Lead,self).create(vals)

    @api.multi
    def write(self, vals):
        res=super(Lead, self).write(vals)
        if self.country_id and self.brand_ids:
            country_id = self.country_id.id
            brand_ids = self.brand_ids.ids
            partner_id = self.partner_id.id
            exist = False
            leads = self.search([('country_id', '=', country_id), ('brand_ids', 'in', brand_ids),('id','!=',self.id)])
            if leads:
                for lead in leads:
                    if lead.partner_id.id == partner_id:
                       exist=True
                if not exist or partner_id == False:
                   raise ValidationError("Restricted,this opportunity with this brand and this country already exist")

        return res

    @api.multi
    @api.constrains('email_from')
    def _check_email_from(self):
        for record in self:
            if not record.partner_id:
                if self.sudo().search([('id', '!=', record.id), ('email_from', '!=', "")]).filtered(
                        lambda p: p.email_from == record.email_from) \
                        or self.env['res.partner'].sudo().search([('email', '!=', "")]).filtered(
                    lambda p: p.email == record.email_from):
                    if self.sudo().search([('id', '!=', record.id), ('email_from', '!=', "")]).filtered(
                        lambda p: p.email_from == record.email_from):

                        created_uid=self.sudo().search([('id', '!=', record.id), ('email_from', '!=', "")]).filtered(
                        lambda p: p.email_from == record.email_from)[0].create_uid.name
                        opp_name=self.sudo().search([('id', '!=', record.id), ('email_from', '!=', "")]).filtered(
                            lambda p: p.email_from == record.email_from)[0].name

                    elif self.env['res.partner'].sudo().search([('email', '!=', "")]).filtered(
                        lambda p: p.email == record.email_from):
                        created_uid = self.env['res.partner'].sudo().search([('email', '!=', "")]).filtered(
                               lambda p: p.email == record.email_from)[0].create_uid.name
                        opp_name = self.env['res.partner'].sudo().search([('email', '!=', "")]).filtered(
                            lambda p: p.email == record.email_from)[0].name
                        #partner=self.env['res.partner'].sudo().search([('email', '!=', "")]).filtered(lambda p: p.email == record.email_from).name

                    raise ValidationError("This customer might be an existing Opportunity/lead in our company ,With Name : %s"
                                          " ,Created by %s has the same Email \n "
                                          ",kindly check with the management" %(opp_name,created_uid))
            '''
            elif record.partner_id:
                if  self.env['res.partner'].sudo().search([('email', '!=', "")]).filtered(lambda p: p.email == record.email_from):
                    raise ValidationError("Email Should be Unique. \n "
                                      "This Lead/Opportunity/Customer might be existing in our company, "
                                      "kindly check with the management")
            '''

    @api.multi
    @api.constrains('mobile')
    def _check_mobile(self):
        for record in self:
            if not record.partner_id:
                if self.sudo().search([('id', '!=', record.id), ('mobile', '!=', "")]).filtered(
                        lambda p: p.mobile == record.mobile) \
                        or self.env['res.partner'].sudo().search([('email', '!=', "")]).filtered(
                    lambda p: p.mobile == record.mobile):
                    if self.sudo().search([('id', '!=', record.id), ('mobile', '!=', "")]).filtered(
                            lambda p: p.mobile == record.mobile):

                        created_uid = self.sudo().search([('id', '!=', record.id), ('mobile', '!=', "")]).filtered(
                            lambda p: p.mobile == record.mobile)[0].create_uid.name
                        opp_name = self.sudo().search([('id', '!=', record.id), ('mobile', '!=', "")]).filtered(
                            lambda p: p.mobile == record.mobile)[0].name

                    elif self.env['res.partner'].sudo().search([('mobile', '!=', "")]).filtered(
                            lambda p: p.mobile == record.mobile):
                        created_uid = self.env['res.partner'].sudo().search([('mobile', '!=', "")]).filtered(
                            lambda p: p.mobile == record.mobile)[0].create_uid.name
                        opp_name = self.env['res.partner'].sudo().search([('mobile', '!=', "")]).filtered(
                            lambda p: p.mobile == record.mobile)[0].name
                        # partner=self.env['res.partner'].sudo().search([('email', '!=', "")]).filtered(lambda p: p.email == record.email_from).name

                    raise ValidationError(
                        "This customer might be an existing Opportunity/lead in our company ,With Name : %s"
                        " ,Created by %s has the same Mobile \n "
                        ",kindly check with the management" % (opp_name, created_uid))

            '''
            elif record.partner_id:
                if  self.env['res.partner'].sudo().search([('mobile', '!=', "")]).filtered(lambda p: p.mobile == record.mobile):
                    raise ValidationError("Mobile Shoud be Unique. \n"
                                      "This Lead/Opportunity/Customer might be an existing in our company, "
                                      "kindly check with the management")
            '''

    @api.multi
    @api.constrains('facebook')
    def _check_facebook(self):
        for record in self:
            if not record.partner_id:
                if self.sudo().search([('id', '!=', record.id), ('facebook', '!=', "")]).filtered(
                        lambda p: p.facebook == record.facebook) \
                        or self.env['res.partner'].sudo().search([('facebook', '!=', "")]).filtered(
                    lambda p: p.facebook == record.facebook):
                    if self.sudo().search([('id', '!=', record.id), ('facebook', '!=', "")]).filtered(
                            lambda p: p.facebook == record.facebook):

                        created_uid = self.sudo().search([('id', '!=', record.id), ('facebook', '!=', "")]).filtered(
                            lambda p: p.facebook == record.facebook)[0].create_uid.name
                        opp_name = self.sudo().search([('id', '!=', record.id), ('facebook', '!=', "")]).filtered(
                            lambda p: p.facebook == record.facebook)[0].name

                    elif self.env['res.partner'].sudo().search([('facebook', '!=', "")]).filtered(
                            lambda p: p.facebook == record.facebook):
                        created_uid = self.env['res.partner'].sudo().search([('facebook', '!=', "")]).filtered(
                            lambda p: p.facebook == record.facebook)[0].create_uid.name
                        opp_name = self.env['res.partner'].sudo().search([('facebook', '!=', "")]).filtered(
                            lambda p: p.facebook == record.facebook)[0].name
                        # partner=self.env['res.partner'].sudo().search([('email', '!=', "")]).filtered(lambda p: p.email == record.email_from).name

                    raise ValidationError(
                        "This customer might be an existing Opportunity/lead in our company ,With Name : %s"
                        " ,Created by %s has the same Facebook \n "
                        ",kindly check with the management" % (opp_name, created_uid))

            '''
            elif record.partner_id:
                if self.env['res.partner'].sudo().search([('facebook', '!=', "")]).filtered(lambda p: p.facebook == record.facebook):
                    raise ValidationError("Facebook Shoud be Unique. \n"
                                          "This Lead/Opportunity/Customer might be an existing in our company, "
                                          "kindly check with the management")
            '''

    @api.multi
    @api.constrains('twitter')
    def _check_twitter(self):
        for record in self:
            if self.sudo().search([('id', '!=', record.id), ('twitter', '!=', "")]).filtered(
                    lambda p: p.twitter == record.twitter) \
                    or self.env['res.partner'].sudo().search([('twitter', '!=', "")]).filtered(
                lambda p: p.twitter == record.twitter):
                if self.sudo().search([('id', '!=', record.id), ('twitter', '!=', "")]).filtered(
                        lambda p: p.twitter == record.twitter):

                    created_uid = self.sudo().search([('id', '!=', record.id), ('twitter', '!=', "")]).filtered(
                        lambda p: p.twitter == record.twitter)[0].create_uid.name
                    opp_name = self.sudo().search([('id', '!=', record.id), ('twitter', '!=', "")]).filtered(
                        lambda p: p.twitter == record.twitter)[0].name

                elif self.env['res.partner'].sudo().search([('twitter', '!=', "")]).filtered(
                        lambda p: p.twitter == record.twitter):
                    created_uid = self.env['res.partner'].sudo().search([('twitter', '!=', "")]).filtered(
                        lambda p: p.twitter == record.twitter)[0].create_uid.name
                    opp_name = self.env['res.partner'].sudo().search([('twitter', '!=', "")]).filtered(
                        lambda p: p.twitter == record.twitter)[0].name
                    # partner=self.env['res.partner'].sudo().search([('email', '!=', "")]).filtered(lambda p: p.email == record.email_from).name

                raise ValidationError(
                    "This customer might be an existing Opportunity/lead in our company ,With Name : %s"
                    " ,Created by %s has the same twitter \n "
                    ",kindly check with the management" % (opp_name, created_uid))

            '''
            elif record.partner_id:
                if self.env['res.partner'].sudo().search([('twitter', '!=', "")]).filtered(
                        lambda p: p.twitter == record.twitter):
                    raise ValidationError("twitter Shoud be Unique. \n"
                                          "This Lead/Opportunity/Customer might be an existing in our company, "
                                          "kindly check with the management")
            '''

    @api.multi
    @api.constrains('linkedin')
    def _check_linkedin(self):
        for record in self:
            if not record.partner_id:
                if self.sudo().search([('id', '!=', record.id), ('linkedin', '!=', "")]).filtered(
                        lambda p: p.linkedin == record.linkedin) \
                        or self.env['res.partner'].sudo().search([('linkedin', '!=', "")]).filtered(
                    lambda p: p.linkedin == record.linkedin):
                    if self.sudo().search([('id', '!=', record.id), ('linkedin', '!=', "")]).filtered(
                            lambda p: p.linkedin == record.linkedin):

                        created_uid = self.sudo().search([('id', '!=', record.id), ('linkedin', '!=', "")]).filtered(
                            lambda p: p.linkedin == record.linkedin)[0].create_uid.name
                        opp_name = self.sudo().search([('id', '!=', record.id), ('linkedin', '!=', "")]).filtered(
                            lambda p: p.linkedin == record.linkedin)[0].name

                    elif self.env['res.partner'].sudo().search([('linkedin', '!=', "")]).filtered(
                            lambda p: p.linkedin == record.linkedin):
                        created_uid = self.env['res.partner'].sudo().search([('linkedin', '!=', "")]).filtered(
                            lambda p: p.linkedin == record.linkedin)[0].create_uid.name
                        opp_name =  self.env['res.partner'].sudo().search([('linkedin', '!=', "")]).filtered(
                            lambda p: p.linkedin == record.linkedin)[0].name
                        # partner=self.env['res.partner'].sudo().search([('email', '!=', "")]).filtered(lambda p: p.email == record.email_from).name

                    raise ValidationError(
                        "This customer might be an existing Opportunity/lead in our company ,With Name : %s"
                        " ,Created by %s has the same linkedin \n "
                        ",kindly check with the management" % (opp_name, created_uid))

            '''
            elif record.partner_id:
                if self.env['res.partner'].sudo().search([('linkedin', '!=', "")]).filtered(
                        lambda p: p.linkedin == record.linkedin):
                    raise ValidationError("linkedin Shoud be Unique. \n"
                                          "This Lead/Opportunity/Customer might be an existing in our company, "
                                          "kindly check with the management")
            '''

    @api.multi
    @api.constrains('instgram')
    def _check_instgram(self):
        for record in self:
            if not record.partner_id:
                if self.sudo().search([('id', '!=', record.id), ('instgram', '!=', "")]).filtered(
                        lambda p: p.instgram == record.instgram) \
                        or self.env['res.partner'].sudo().search([('instgram', '!=', "")]).filtered(
                    lambda p: p.instgram == record.instgram):
                    if self.sudo().search([('id', '!=', record.id), ('instgram', '!=', "")]).filtered(
                            lambda p: p.instgram == record.instgram):

                        created_uid = self.sudo().search([('id', '!=', record.id), ('instgram', '!=', "")]).filtered(
                            lambda p: p.instgram == record.instgram)[0].create_uid.name
                        opp_name = self.sudo().search([('id', '!=', record.id), ('instgram', '!=', "")]).filtered(
                            lambda p: p.instgram == record.instgram)[0].name

                    elif self.env['res.partner'].sudo().search([('instgram', '!=', "")]).filtered(
                            lambda p: p.instgram == record.instgram):
                        created_uid = self.env['res.partner'].sudo().search([('instgram', '!=', "")]).filtered(
                            lambda p: p.instgram == record.instgram)[0].create_uid.name
                        opp_name=self.env['res.partner'].sudo().search([('instgram', '!=', "")]).filtered(
                            lambda p: p.instgram == record.instgram)[0].name
                        # partner=self.env['res.partner'].sudo().search([('email', '!=', "")]).filtered(lambda p: p.email == record.email_from).name

                    raise ValidationError(
                        "This customer might be an existing Opportunity/lead in our company ,With Name : %s"
                        " ,Created by %s has the same instgram \n "
                        ",kindly check with the management" % (opp_name, created_uid))

            '''
            elif record.partner_id:
                if self.env['res.partner'].sudo().search([('instgram', '!=', "")]).filtered(
                        lambda p: p.instgram == record.instgram):
                    raise ValidationError("instgram Shoud be Unique. \n"
                                          "This Lead/Opportunity/Customer might be an existing in our company, "
                                          "kindly check with the management")
            '''

    @api.multi
    @api.constrains('website')
    def _check_website(self):
        for record in self:
            if not record.partner_id:
                if self.sudo().search([('id', '!=', record.id), ('website', '!=', "")]).filtered(
                        lambda p: p.website == record.website) \
                        or self.env['res.partner'].sudo().search([('website', '!=', "")]).filtered(
                    lambda p: p.website == record.website):
                    if self.sudo().search([('id', '!=', record.id), ('website', '!=', "")]).filtered(
                            lambda p: p.website == record.website):

                        created_uid = self.sudo().search([('id', '!=', record.id), ('website', '!=', "")]).filtered(
                            lambda p: p.website == record.website)[0].create_uid.name
                        opp_name = self.sudo().search([('id', '!=', record.id), ('website', '!=', "")]).filtered(
                            lambda p: p.website == record.website)[0].name

                    elif self.env['res.partner'].sudo().search([('website', '!=', "")]).filtered(
                            lambda p: p.website == record.website):
                        created_uid = self.env['res.partner'].sudo().search([('website', '!=', "")]).filtered(
                            lambda p: p.website == record.website)[0].create_uid.name
                        opp_name=self.env['res.partner'].sudo().search([('website', '!=', "")]).filtered(
                            lambda p: p.website == record.website)[0].name
                        # partner=self.env['res.partner'].sudo().search([('email', '!=', "")]).filtered(lambda p: p.email == record.email_from).name

                    raise ValidationError(
                        "This customer might be an existing Opportunity/lead in our company ,With Name : %s"
                        " ,Created by %s has the same website \n "
                        ",kindly check with the management" % (opp_name, created_uid))

            '''
            elif record.partner_id:
                if self.env['res.partner'].sudo().search([('website', '!=', "")]).filtered(
                        lambda p: p.website == record.website):
                    raise ValidationError("website Shoud be Unique. \n"
                                          "This Lead/Opportunity/Customer might be an existing in our company, "
                                          "kindly check with the management")
            '''

    @api.multi
    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if not record.partner_id:
                if self.sudo().search([('id', '!=', record.id), ('phone', '!=', "")]).filtered(
                        lambda p: p.phone == record.phone) \
                        or self.env['res.partner'].sudo().search([('phone', '!=', "")]).filtered(
                    lambda p: p.phone == record.phone):
                    if self.sudo().search([('id', '!=', record.id), ('phone', '!=', "")]).filtered(
                            lambda p: p.phone == record.phone):

                        created_uid = self.sudo().search([('id', '!=', record.id), ('phone', '!=', "")]).filtered(
                            lambda p: p.phone == record.phone)[0].create_uid.name
                        opp_name = self.sudo().search([('id', '!=', record.id), ('phone', '!=', "")]).filtered(
                            lambda p: p.phone == record.phone)[0].name

                    elif self.env['res.partner'].sudo().search([('phone', '!=', "")]).filtered(
                            lambda p: p.phone == record.phone):
                        created_uid = self.env['res.partner'].sudo().search([('phone', '!=', "")]).filtered(
                            lambda p: p.phone == record.phone)[0].create_uid.name
                        opp_name=self.env['res.partner'].sudo().search([('phone', '!=', "")]).filtered(
                            lambda p: p.phone == record.phone)[0].name
                        # partner=self.env['res.partner'].sudo().search([('email', '!=', "")]).filtered(lambda p: p.email == record.email_from).name

                    raise ValidationError(
                        "This customer might be an existing Opportunity/lead in our company ,With Name : %s"
                        " ,Created by %s has the same phone \n "
                        ",kindly check with the management" % (opp_name, created_uid))

            '''
            elif record.partner_id:
                if self.env['res.partner'].sudo().search([('phone', '!=', "")]).filtered(
                        lambda p: p.phone == record.phone):
                    raise ValidationError("phone Shoud be Unique. \n"
                                          "This Lead/Opportunity/Customer might be an existing in our company, "
                                          "kindly check with the management")
            '''

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for record in self:
            if record.partner_id:
                record.brand_ids = record.partner_id.brand_ids
                record.country_group_id = record.partner_id.country_group_id
                record.country_id = record.partner_id.country_id
                record.state_id = record.partner_id.state_id
                record.mobile = record.partner_id.mobile
                record.fax = record.partner_id.fax
                record.phone = record.partner_id.phone
                record.city = record.partner_id.city
                record.zip = record.partner_id.zip
                record.street2 = record.partner_id.street2
                record.street = record.partner_id.street
                record.email_from = record.partner_id.email
                record.facebook = record.partner_id.facebook
                record.twitter = record.partner_id.twitter
                record.linkedin = record.partner_id.linkedin
                record.instgram = record.partner_id.instgram
                record.website = record.partner_id.website
                record.user_type = record.partner_id.user_type
                if record.partner_id.child_ids:
                   record.contact_name = record.partner_id.child_ids[0].name
                   record.contact_mobile=record.partner_id.child_ids[0].mobile

    @api.depends('margin_value', 'planned_revenue')
    @api.multi
    def _compute_margin(self):
        for lead in self:
            if lead.planned_revenue != 0:
                lead.margin = (lead.margin_value / lead.planned_revenue) * 100

    @api.depends('margin', 'container')
    @api.multi
    def _compute_margin_aed_container(self):
        for lead in self:
            if lead.container != 0:
                lead.margin_aed_container = lead.margin_value / lead.container

    @api.multi
    def _lead_create_contact(self, name, is_company, parent_id=False):
        """ extract data from lead to create a partner
            :param name : furtur name of the partner
            :param is_company : True if the partner is a company
            :param parent_id : id of the parent partner (False if no parent)
            :returns res.partner record
        """
        email_split = tools.email_split(self.email_from)
        lead = self.browse(self.env.context.get('active_id'))
        values = {
            'name': name,
            'user_id': self.env.context.get('default_user_id') or lead.user_id.id,
            'comment': lead.description,
            'team_id': lead.team_id.id,
            'parent_id': parent_id,
            'phone': lead.phone,
            'mobile': lead.mobile,
            'email': email_split[0] if email_split else lead.email_from,
            'fax': lead.fax,
            'title': lead.title.id,
            'function': lead.function,
            'street': lead.street,
            'street2': lead.street2,
            'zip': lead.zip,
            'city': lead.city,
            'country_id': lead.country_id.id,
            'state_id': lead.state_id.id,
            'is_company': is_company,
            'type': 'contact',
            'facebook': lead.facebook,
            'twitter': lead.twitter,
            'linkedin': lead.linkedin,
            'instgram': lead.instgram,
            'country_group_id': lead.country_group_id.id,
            'contact_name':lead.contact_name,
            'contact_mobile': lead.mobile,

        }
        return self.env['res.partner'].create(values)

    @api.model
    def retrieve_sales_dashboard(self):
        """ Fetch data to setup Sales Dashboard """
        result = {
            'meeting': {
                'today': 0,
                'next_7_days': 0,
            },
            'activity': {
                'today': 0,
                'overdue': 0,
                'next_7_days': 0,
            },
            'closing': {
                'today': 0,
                'overdue': 0,
                'next_7_days': 0,
            },
            'done': {
                'this_month': 0,
                'last_month': 0,
            },
            'won': {
                'this_month': 0,
                'last_month': 0,
            },
            'nb_opportunities': 0,
        }

        opportunities = self.search([('type', '=', 'opportunity'), ('user_id', '=', self._uid)])

        for opp in opportunities:
            # Expected closing
            if opp.date_deadline:
                date_deadline = fields.Date.from_string(opp.date_deadline)
                if date_deadline == date.today():
                    result['closing']['today'] += 1
                if date.today() <= date_deadline <= date.today() + timedelta(days=7):
                    result['closing']['next_7_days'] += 1
                if date_deadline < date.today():
                    result['closing']['overdue'] += 1
            # Next activities
            if opp.next_activity_id and opp.date_action:
                date_action = fields.Date.from_string(opp.date_action)
                if date_action == date.today():
                    result['activity']['today'] += 1
                if date.today() <= date_action <= date.today() + timedelta(days=7):
                    result['activity']['next_7_days'] += 1
                if date_action < date.today():
                    result['activity']['overdue'] += 1
            # Won in Opportunities
            if opp.date_closed:
                date_closed = fields.Date.from_string(opp.date_closed)
                if date.today().replace(day=1) <= date_closed <= date.today():
                    # if opp.planned_revenue:
                    if opp.margin_value:
                        result['won']['this_month'] += opp.margin_value
                elif date.today() + relativedelta(months=-1, day=1) <= date_closed < date.today().replace(day=1):
                    # if opp.planned_revenue:
                    if opp.margin_value:
                        result['won']['last_month'] += opp.margin_value

        result['nb_opportunities'] = len(opportunities)

        # crm.activity is a very messy model so we need to do that in order to retrieve the actions done.
        self._cr.execute("""
                   SELECT
                       m.id,
                       m.subtype_id,
                       m.date,
                       l.user_id,
                       l.type
                   FROM mail_message M
                       LEFT JOIN crm_lead L ON (M.res_id = L.id)
                       INNER JOIN crm_activity A ON (M.subtype_id = A.subtype_id)
                   WHERE
                       (M.model = 'crm.lead') AND (L.user_id = %s) AND (L.type = 'opportunity')
               """, (self._uid,))
        activites_done = self._cr.dictfetchall()

        for activity in activites_done:
            if activity['date']:
                date_act = fields.Date.from_string(activity['date'])
                if date.today().replace(day=1) <= date_act <= date.today():
                    result['done']['this_month'] += 1
                elif date.today() + relativedelta(months=-1, day=1) <= date_act < date.today().replace(day=1):
                    result['done']['last_month'] += 1

        # Meetings
        min_date = fields.Datetime.now()
        max_date = fields.Datetime.to_string(datetime.now() + timedelta(days=8))
        meetings_domain = [
            ('start', '>=', min_date),
            ('start', '<=', max_date),
            ('partner_ids', 'in', [self.env.user.partner_id.id])
        ]
        meetings = self.env['calendar.event'].search(meetings_domain)
        for meeting in meetings:
            if meeting['start']:
                start = datetime.strptime(meeting['start'], tools.DEFAULT_SERVER_DATETIME_FORMAT).date()
                if start == date.today():
                    result['meeting']['today'] += 1
                if date.today() <= start <= date.today() + timedelta(days=7):
                    result['meeting']['next_7_days'] += 1

        result['done']['target'] = self.env.user.target_sales_done
        result['won']['target'] = self.env.user.target_sales_won
        result['currency_id'] = self.env.user.company_id.currency_id.id

        return result




class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.multi
    def compute_fiscalyear_dates(self, current_date):
        print ('dddddddddddd')
        '''Computes the start and end dates of the fiscal year where the given 'date' belongs to.

        :param current_date: A datetime.date/datetime.datetime object.
        :return: A dictionary containing:
            * date_from
            * date_to
            * [Optionally] record: The fiscal year record.
        '''
        if current_date:
            self.ensure_one()
            date_str = current_date.strftime(DEFAULT_SERVER_DATE_FORMAT)

            # Search a fiscal year record containing the date.
            # If a record is found, then no need further computation, we get the dates range directly.
            fiscalyear = self.env['account.fiscal.year'].search([
                ('company_id', '=', self.id),
                ('date_from', '<=', date_str),
                ('date_to', '>=', date_str),
            ], limit=1)
            if fiscalyear:
                return {
                    'date_from': fiscalyear.date_from,
                    'date_to': fiscalyear.date_to,
                    'record': fiscalyear,
                }

            date_from, date_to = date_utils.get_fiscal_year(
                current_date, day=self.fiscalyear_last_day, month=self.fiscalyear_last_month)

            date_from_str = date_from.strftime(DEFAULT_SERVER_DATE_FORMAT)
            date_to_str = date_to.strftime(DEFAULT_SERVER_DATE_FORMAT)

            # Search for fiscal year records reducing the delta between the date_from/date_to.
            # This case could happen if there is a gap between two fiscal year records.
            # E.g. two fiscal year records: 2017-01-01 -> 2017-02-01 and 2017-03-01 -> 2017-12-31.
            # => The period 2017-02-02 - 2017-02-30 is not covered by a fiscal year record.

            fiscalyear_from = self.env['account.fiscal.year'].search([
                ('company_id', '=', self.id),
                ('date_from', '<=', date_from_str),
                ('date_to', '>=', date_from_str),
            ], limit=1)
            if fiscalyear_from:
                date_from = fiscalyear_from.date_to + timedelta(days=1)

            fiscalyear_to = self.env['account.fiscal.year'].search([
                ('company_id', '=', self.id),
                ('date_from', '<=', date_to_str),
                ('date_to', '>=', date_to_str),
            ], limit=1)
            if fiscalyear_to:
                date_to = fiscalyear_to.date_from - timedelta(days=1)

            return {'date_from': date_from, 'date_to': date_to}

