# -*- coding: utf-8 -*-
{
    'name': "Purchase Agreement Multi Vendor",


    'description': """
        Add ability to create Purchase Agreement with Multi Vendor
    """,

    'author': "Netaq Team",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase_requisition'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}