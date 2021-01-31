# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Armor Templates',
    'version': '12.0.0.1',
    'summary': '',
    'category': 'Tools',
    'description': """
		Customize report, customize pdf report, customize template report, Customize Sales Order report,Customize Purchase Order report, Customize invoice report, Accounting Reports.
		
    """,
    'license': 'OPL-1',
    'author': 'SmartData',
    'website': '',
    'depends': ['base', 'account', 'sale', 'stock', 'purchase','hr', 'analytic_account_changes', 'sale_with_bom', 'product','changes_delivery_order'],
    'data': [
        'security/ir.model.access.csv',
        "views/views.xml",
        "views.xml",
        "sale_report/classic_sale_report.xml",
        "sale_report/classic_report_saleorder.xml",
        "purchase_report/classic_purchase_report.xml",
        "purchase_report/classic_report_purchaseorder.xml",
        "invoice_report/classic_invoice_report.xml",
        "invoice_report/classic_report_invoice.xml",
        "delivery_report/stock_report_classic.xml",
        "delivery_report/odoo_standard_report_deliveryslip.xml",

    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    "images": [],
}
