# -*- coding: utf-8 -*-

{
    'name': 'Partner Report',
    'summary': """Partner Report""",
    'version': '13.0.1.0',
    'description': """Partner Report""",
    'author': 'Mostafa Abbas',
    # 'company': '',
    # 'website': '',
    # 'category': 'Point of Sale',
    'depends': ['base','sale','purchase','account'],
    'license': 'AGPL-3',
    'data': [
        # 'reports/pos_session_report.xml',
        # 'security/ir.model.access.csv',

        'wizard/sale_purchase_wizard.xml',
        'wizard/invoices_bills_wizard.xml',
        'wizard/product_wizard.xml',

        'reports/invoices_bills_reports.xml',
        'reports/product_report.xml',
        'reports/sale_purchase_reports.xml',
    ],
    # 'images': ['static/description/banner.jpg'],
    # 'demo': [],
    'installable': True,
    'auto_install': False,

}
