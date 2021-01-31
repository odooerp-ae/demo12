# -*- coding: utf-8 -*-
{
    'name': "Fields Based on Product Category",

    'description': """
    """,

    'author': "Netaq Team",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Product',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'security/groups_data.xml',
        'views/product_category_view.xml',
        'views/product_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
      #  'demo/demo.xml',
    ],
}
