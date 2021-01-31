# -*- encoding: utf-8 -*-

{
    'name': 'SMTP Server Per User',
    'category': 'Mail',
    'author': 'TKOPEN',
    'license': 'AGPL-3',
    'website': 'https://tkopen.com',
    'version': '12.0.1',
    'sequence': 10,
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'init': [],
    'demo': [],
    'update': [],
    "images": ['static/description/thumbnail.png'],
    'test': [],  # YAML files with tests
    'installable': True,
    'application': False,
    'auto_install': False,
    'certificate': '',
}
