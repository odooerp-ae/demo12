# -*- coding: utf-8 -*-
{
    'name': "Armor",
    'version': '12.0.1.0.0',
    'summary': """2 Levels Mrp.""",
    'description': """2 Levels Mrp.""",
    'category': 'MRP',
    'depends': ['base', 'product','sale','mrp'],
    'data': [
        'views/sale.xml',
        'views/bom.xml',
        'views/product_view.xml',
        'views/mrp_templates.xml',
        'views/mrp_production_inherit_view.xml',
        'report/mrp_report_bom_structure.xml',
        'wizard/check_mo.xml',
    ],
    'qweb': ['static/src/xml/mrp.xml'],

    'price': 9.99,
    'installable': True,
    'auto_install': False,
    'application': False,
}
