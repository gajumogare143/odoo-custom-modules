from odoo import models, fields, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    whatsapp_receipt_sent = fields.Boolean('WhatsApp Receipt Sent', default=False)
    whatsapp_message_id = fields.Char('WhatsApp Message ID')
    
    def action_send_whatsapp_receipt(self):
        """Send POS receipt via WhatsApp"""
        self.ensure_one()
        
        if not self.partner_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Warning'),
                    'message': _('No customer selected for this order.'),
                    'type': 'warning',
                }
            }
        
        if not self.partner_id.whatsapp_number:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Warning'),
                    'message': _('Customer does not have a WhatsApp number.'),
                    'type': 'warning',
                }
            }
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Send WhatsApp Receipt'),
            'res_model': 'pos.whatsapp.receipt',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_pos_order_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_to_number': self.partner_id.whatsapp_number,
            }
        }
    
    def get_receipt_text(self):
        """Generate receipt text for WhatsApp"""
        self.ensure_one()
        
        lines = []
        lines.append(f"🧾 *{self.company_id.name}*")
        lines.append(f"📅 Date: {self.date_order.strftime('%d/%m/%Y %H:%M')}")
        lines.append(f"🔢 Order: {self.name}")
        lines.append("")
        lines.append("📋 *Items:*")
        
        for line in self.lines:
            item_line = f"• {line.product_id.name}"
            if line.qty != 1:
                item_line += f" x{line.qty}"
            item_line += f" - ₹{line.price_subtotal_incl:.2f}"
            lines.append(item_line)
        
        lines.append("")
        lines.append(f"💰 *Total: ₹{self.amount_total:.2f}*")
        
        if self.amount_paid:
            lines.append(f"💳 Paid: ₹{self.amount_paid:.2f}")
        
        lines.append("")
        lines.append("Thank you for your business! 🙏")
        
        return "\n".join(lines)