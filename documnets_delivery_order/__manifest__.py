# -*- coding: utf-8 -*-
{
    'name': "Documents On Delivery Order",

    'description': """
    """,

    'author': "Netaq Team",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'sale', 'sale_stock', 'purchase','base','contacts','armor_opportunity_modifications'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_view.xml',
        'views/sale_order_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
