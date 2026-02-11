import json
import logging
import hmac
import hashlib
from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)


class WhatsAppWebhook(http.Controller):

    @http.route('/whatsapp/webhook', type='http', auth='none', methods=['GET', 'POST'], csrf=False)
    def whatsapp_webhook(self, **kwargs):
        """Handle WhatsApp webhook requests"""
        
        if request.httprequest.method == 'GET':
            return self._verify_webhook()
        elif request.httprequest.method == 'POST':
            return self._handle_webhook_message()
    
    def _verify_webhook(self):
        """Verify webhook during setup"""
        try:
            mode = request.params.get('hub.mode')
            token = request.params.get('hub.verify_token')
            challenge = request.params.get('hub.challenge')
            
            if mode == 'subscribe':
                # Find business account with matching verify token
                business_account = request.env['whatsapp.business.account'].sudo().search([
                    ('webhook_verify_token', '=', token)
                ], limit=1)
                
                if business_account:
                    _logger.info(f"Webhook verified for account: {business_account.name}")
                    return challenge
                else:
                    _logger.warning(f"Webhook verification failed - invalid token: {token}")
                    return "Invalid verify token", 403
            
            return "Invalid mode", 400
            
        except Exception as e:
            _logger.error(f"Webhook verification error: {str(e)}")
            return "Verification failed", 500
    
    def _handle_webhook_message(self):
        """Handle incoming webhook messages"""
        try:
            # Get request data
            body = request.httprequest.get_data(as_text=True)
            signature = request.httprequest.headers.get('X-Hub-Signature-256', '')
            
            # Parse JSON data
            data = json.loads(body)
            
            # Process webhook data
            if data.get('object') == 'whatsapp_business_account':
                for entry in data.get('entry', []):
                    self._process_webhook_entry(entry, body)
            
            return "OK"
            
        except Exception as e:
            _logger.error(f"Webhook processing error: {str(e)}")
            return "Processing failed", 500
    
    def _verify_signature(self, body, signature, business_account):
        """Verify webhook signature"""
        try:
            if not business_account.webhook_verify_token:
                return True  # Skip verification if no token set
            
            expected_signature = 'sha256=' + hmac.new(
                business_account.webhook_verify_token.encode('utf-8'),
                body.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            _logger.error(f"Signature verification error: {str(e)}")
            return False
    
    def _process_webhook_entry(self, entry, raw_data):
        """Process individual webhook entry"""
        try:
            business_account_id = entry.get('id')
            
            # Find business account
            business_account = request.env['whatsapp.business.account'].sudo().search([
                ('business_account_id', '=', business_account_id)
            ], limit=1)
            
            if not business_account:
                _logger.warning(f"Business account not found: {business_account_id}")
                return
            
            # Process changes
            for change in entry.get('changes', []):
                field = change.get('field')
                value = change.get('value', {})
                
                if field == 'messages':
                    self._process_message_webhook(business_account, value, raw_data)
                elif field == 'message_deliveries':
                    self._process_delivery_webhook(business_account, value)
                
        except Exception as e:
            _logger.error(f"Entry processing error: {str(e)}")
    
    def _process_message_webhook(self, business_account, value, raw_data):
        """Process incoming message webhook"""
        try:
            messages = value.get('messages', [])
            
            for message_data in messages:
                message_id = message_data.get('id')
                from_number = message_data.get('from')
                timestamp = message_data.get('timestamp')
                message_type = message_data.get('type', 'text')
                
                # Get message content based on type
                content = ''
                if message_type == 'text':
                    content = message_data.get('text', {}).get('body', '')
                elif message_type == 'image':
                    content = f"Image: {message_data.get('image', {}).get('caption', 'No caption')}"
                elif message_type == 'document':
                    content = f"Document: {message_data.get('document', {}).get('filename', 'Unknown')}"
                
                # Find or create partner
                partner = request.env['res.partner'].sudo().find_partner_by_whatsapp(from_number)
                
                # Create message record
                request.env['whatsapp.message'].sudo().create({
                    'business_account_id': business_account.id,
                    'message_id': message_id,
                    'partner_id': partner.id if partner else False,
                    'from_number': from_number,
                    'message_type': message_type,
                    'content': content,
                    'status': 'received',
                    'direction': 'inbound',
                    'webhook_data': raw_data
                })
                
                _logger.info(f"Incoming message processed: {message_id}")
                
        except Exception as e:
            _logger.error(f"Message webhook processing error: {str(e)}")
    
    def _process_delivery_webhook(self, business_account, value):
        """Process message delivery status webhook"""
        try:
            statuses = value.get('statuses', [])
            
            for status_data in statuses:
                message_id = status_data.get('id')
                status = status_data.get('status')  # sent, delivered, read, failed
                
                # Update message status
                message = request.env['whatsapp.message'].sudo().search([
                    ('message_id', '=', message_id),
                    ('business_account_id', '=', business_account.id)
                ], limit=1)
                
                if message:
                    message.status = status
                    _logger.info(f"Message status updated: {message_id} -> {status}")
                
        except Exception as e:
            _logger.error(f"Delivery webhook processing error: {str(e)}")