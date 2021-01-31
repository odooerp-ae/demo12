# -*- coding: utf-8 -*-
{
    'name': "Internal Transfer",

    'summary': """
        make internal transfer between more than location""",

    'description': """
        Long description of module's purpose
    """,

    'author': "G2mdx",
    'website': "http://www.G2mdx.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail','purchase','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/request_delivery.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}