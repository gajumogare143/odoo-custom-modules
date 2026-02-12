{
    'name': 'Meta WhatsApp Business API Integration',
    'version': '18.0.1.0.0',
    'category': 'Marketing',
    'summary': 'WhatsApp Business API integration using Meta API for Odoo 18',
    'description': '''
        Meta WhatsApp Business API Integration for Odoo 18
        ================================================

        Features:
        * Send WhatsApp messages using Meta Business API
        * Template message support
        * Contact management with WhatsApp numbers
        * Webhook support for incoming messages
        * Multiple WhatsApp Business Account support
        * Message history and tracking
        * POS receipt sharing via WhatsApp

        Requirements:
        * Meta WhatsApp Business API access
        * Valid WhatsApp Business Account
        * Webhook endpoint configuration
    ''',
    'author': 'Custom Development',
    'website': 'https://developers.facebook.com/docs/whatsapp',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'contacts', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/whatsapp_templates.xml',
        'views/whatsapp_business_account_views.xml',
        'views/whatsapp_message_views.xml',
        'views/whatsapp_template_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
        'wizard/send_whatsapp_message_views.xml',
        'wizard/pos_whatsapp_receipt_views.xml',
        'views/pos_order_views.xml',
        'views/sales_order_views.xml',
        'views/purchase_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'meta_whatsapp_integration/static/src/css/whatsapp.css',
            'meta_whatsapp_integration/static/src/js/pos_whatsapp_button.js'
        ],
        'point_of_sale.assets': [
            'meta_whatsapp_integration/static/src/js/pos_whatsapp.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
