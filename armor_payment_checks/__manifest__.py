# -*- coding: utf-8 -*-
{
    'name': "Armor Payment Checks",

    'author': "Netaq Team",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account', 'account_accountant', 'account_reports'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/account_data_view.xml',
        'wizard/account_payment_deposit_check_wizard.xml',
        'wizard/account_payment_reject_wizard.xml',
        'views/views.xml',
    ],

}
