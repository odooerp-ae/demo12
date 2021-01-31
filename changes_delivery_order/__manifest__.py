# -*- coding: utf-8 -*-
{
    'name': "Changes On Delivery Order",

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
    'depends': ['stock', 'product', 'sale'],

    # always loaded
    'data': [
        'report/stock_report_views.xml',
        'report/report_stockpicking_pickinglist.xml',
        'views/product_view.xml',
        'views/stock_picking_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
