from odoo import models, fields, api, _
from odoo.exceptions import UserError
import re


class PosOrder(models.Model):
    _inherit = 'pos.order'

    whatsapp_receipt_sent = fields.Boolean('WhatsApp Receipt Sent', default=False)
    whatsapp_message_id = fields.Char('WhatsApp Message ID')

    # =====================================================
    # Send WhatsApp Receipt (Called from POS JS)
    # =====================================================
    def action_send_whatsapp_receipt(self, number=None):
        self.ensure_one()

        # If number passed from POS screen
        if number:
            whatsapp_number = number
        else:
            if not self.partner_id:
                raise UserError(_("No customer selected for this order."))

            if not self.partner_id.whatsapp_number:
                raise UserError(_("Customer does not have a WhatsApp number."))

            whatsapp_number = self.partner_id.whatsapp_number

        # Clean number
        whatsapp_number = re.sub(r'[^\d+]', '', whatsapp_number)

        if not whatsapp_number:
            raise UserError(_("Invalid WhatsApp number."))

        # Generate receipt text
        message_body = self.get_receipt_text()

        # Create WhatsApp message record
        message = self.env['whatsapp.message'].create({
            'partner_id': self.partner_id.id if self.partner_id else False,
            'to_number': whatsapp_number,
            'message_type': 'text',
            'body': message_body,
            'state': 'draft',
        })

        # Call your existing send logic
        message.action_send_whatsapp_message()

        self.whatsapp_receipt_sent = True
        self.whatsapp_message_id = message.message_id if hasattr(message, 'message_id') else False

        return True

    # =====================================================
    # Generate Receipt Text
    # =====================================================
    def get_receipt_text(self):
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