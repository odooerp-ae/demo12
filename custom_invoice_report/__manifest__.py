{
    'name': 'Custom Invoice Report',
    'category': 'custom report',
    'author': 'Netaq Team',
    'description': """
    Add More Bank Details in Invoice Report
""",
    'depends': [
        'base',
        'stock',
        'account',
    ],
    'data': [
        'views/custom_invoice_report.xml',
        'views/account_journal_view.xml',
    ],
    'installable': True,

}
