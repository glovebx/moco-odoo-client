# -*- coding: utf-8 -*-

{
    'name': 'Mail Mobile Push',
    'version': '1.0',
    'category': 'Hidden/Tools',
    'summary': 'Provides push notification to the mobile app.',
    'website': 'https://github.com/glovebx/moco-odoo-client',
    'description': """
Mail Mobile Push
===========
This module modifies the mail addon to provide:

* Push notifications to registered devices for direct messages, chatter messages and channel.
    """,
    'depends': [
        'base_setup',
    ],
    'data': [
        'data/mail_mobile_push_data.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'auto_install': [],
    'license': 'LGPL-3',
    'assets': {

    }
}
