# -*- coding: utf-8 -*-
{
    'name': "Armor Opportunity Modifications",

    'summary': """
        """,

    'description': """
    """,

    'author': "Mona Zakaria",
    'website': "monazakria2015@gmail.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'CRM',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm','stock', 'voip', 'sale_management'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead.xml',
        # 'wizard/crm_phonecall_log_wizard.xml',
        # 'views/hepdesk_ticket_view.xml',
        'views/res_users_view.xml',
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
    ],
    'qweb': [
            "static/src/xml/sales_dashboard.xml",
    ],

}