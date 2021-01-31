# -*- coding: utf-8 -*-
{
    'name': "Partner Restriction",

    'description': """
    """,

    'author': "",
    'website': "",

    'category': 'Base',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_management','sale_crm','crm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order.xml',
        'views/crm.xml',
        'views/account_invoice.xml',
        # 'views/config.xml',
        'wizard/assign_users_wizard.xml',
        'views/partner.xml'
    ],
    # only loaded in demonstration mode
    'demo': [],
    'qweb': [

    ],
}
