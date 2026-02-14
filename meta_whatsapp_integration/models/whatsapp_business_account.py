import requests
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WhatsAppBusinessAccount(models.Model):
    _name = 'whatsapp.business.account'
    _description = 'WhatsApp Business Account'
    _rec_name = 'name'

    # Fields
    name = fields.Char('Account Name', required=True)
    phone_number_id = fields.Char('Phone Number ID', required=True)
    access_token = fields.Char('Access Token', required=True)
    business_account_id = fields.Char('Business Account ID', required=True)
    webhook_verify_token = fields.Char('Webhook Verify Token')
    phone_number = fields.Char('Phone Number', readonly=True)
    display_name = fields.Char('Display Name', readonly=True)
    status = fields.Selection([
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error')
    ], string='Status', default='disconnected', readonly=True)
    is_default = fields.Boolean('Default Account', default=False)
    active = fields.Boolean('Active', default=True)

    # API Config
    api_version = fields.Char('API Version', default='v18.0')
    base_url = fields.Char('Base URL', default='https://graph.facebook.com')

    # Statistics
    messages_sent_today = fields.Integer('Messages Sent Today', readonly=True)
    last_message_date = fields.Datetime('Last Message Date', readonly=True)

    # Create / Write overrides for default account
    @api.model
    def create(self, vals):
        if vals.get('is_default'):
            self.search([('is_default', '=', True)]).write({'is_default': False})
        return super().create(vals)

    def write(self, vals):
        if vals.get('is_default'):
            self.search([('id', '!=', self.id), ('is_default', '=', True)]).write({'is_default': False})
        return super().write(vals)

    # Action: Test connection
    def action_test_connection(self):
        self.ensure_one()
        try:
            url = f"{self.base_url}/{self.api_version}/{self.phone_number_id}"
            headers = {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json'}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                self.write({
                    'status': 'connected',
                    'phone_number': data.get('display_phone_number', ''),
                    'display_name': data.get('name', ''),
                })
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {'title': _('Success'), 'message': _('WhatsApp Business API connection successful!'), 'type': 'success'}
                }
            else:
                self.status = 'error'
                raise UserError(_('Connection failed: %s') % response.text)

        except Exception as e:
            self.status = 'error'
            _logger.error(f"WhatsApp API connection error: {str(e)}")
            raise UserError(_('Connection error: %s') % str(e))

    # Action: View messages (new method)
    def action_view_messages(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Messages'),
            'res_model': 'whatsapp.message',  # <-- तुमच्या Messages model चा name
            'view_mode': 'list,form',
            'domain': [('business_account_id', '=', self.id)],
            'context': {'default_business_account_id': self.id},
        }

    # Action: Set as default
    def action_set_as_default(self):
        self.ensure_one()
        self.search([('is_default', '=', True)]).write({'is_default': False})
        self.is_default = True
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'title': _('Success'), 'message': _('Account set as default successfully!'), 'type': 'success'}
        }

    # Send WhatsApp message
    def send_message(self, to_number, message_type='text', **kwargs):
        self.ensure_one()
        if self.status != 'connected':
            raise UserError(_('WhatsApp account is not connected. Please test connection first.'))

        url = f"{self.base_url}/{self.api_version}/{self.phone_number_id}/messages"
        headers = {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json'}
        clean_number = ''.join(filter(str.isdigit, to_number))
        if not clean_number.startswith('91'):
            clean_number = '91' + clean_number

        payload = {'messaging_product': 'whatsapp', 'to': clean_number, 'type': message_type}
        if message_type == 'text':
            payload['text'] = {'body': kwargs.get('text', '')}
        elif message_type == 'template':
            payload['template'] = kwargs.get('template', {})
        elif message_type == 'document':
            payload['document'] = kwargs.get('document', {})

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                message_id = result.get('messages', [{}])[0].get('id')
                self.messages_sent_today += 1
                self.last_message_date = fields.Datetime.now()

                self.env['whatsapp.message'].create({
                    'business_account_id': self.id,
                    'message_id': message_id,
                    'to_number': clean_number,
                    'message_type': message_type,
                    'content': kwargs.get('text', '') or str(kwargs),
                    'status': 'sent',
                    'direction': 'outbound'
                })

                return {'success': True, 'message_id': message_id, 'response': result}
            else:
                error_msg = response.json().get('error', {}).get('message', response.text)
                _logger.error(f"WhatsApp send message error: {error_msg}")
                return {'success': False, 'error': error_msg}

        except Exception as e:
            _logger.error(f"WhatsApp API error: {str(e)}")
            return {'success': False, 'error': str(e)}

    # Get default account
    @api.model
    def get_default_account(self):
        account = self.search([('is_default', '=', True), ('active', '=', True)], limit=1)
        if not account:
            account = self.search([('active', '=', True)], limit=1)
        return account
