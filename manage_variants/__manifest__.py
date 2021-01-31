# -*- coding: utf-8 -*-
{
    'name': "Manage Variants",

    'description': """
    """,

    'author': "SmartData Team",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'product',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product'],

    # always loaded
    'data': [
        'views/product_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'qweb': [],
}
