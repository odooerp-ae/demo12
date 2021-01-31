{
    'name': "Account Invoice Report",
    'author': "Netaq Team",
    'category': "Accounting",
    'data': [
        'views/alkendi_report_invoice.xml',
        'views/res_company_view.xml',
        'views/layouts.xml',
        'views/report_invoice.xml',
    ],
    'demo': [],
    'depends': ['account', 'custom_invoice_report'],
    'installable': True,
}