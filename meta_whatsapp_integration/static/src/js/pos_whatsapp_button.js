/** @odoo-module */
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";

patch(ReceiptScreen.prototype, {
    setup() {
        super.setup(...arguments);
        const partner = this.currentOrder.get_partner();
        const orderName = this.currentOrder.name || '';
        let number = '';
        if (partner) {
            number = partner.phone || partner.mobile || '';
        }
        this.orderUiState = useState({
            inputWhatsapp: number,
            inputMessage: `Hello, here is your receipt for order: ${orderName}`,
            isSending: false,
            whatsappButtonDisabled: false,
        });
    },

    is_valid_mobile() {
        const value = this.orderUiState.inputWhatsapp || '';
        const valueLen = value.replace(/[^0-9]/g, '').length;
        return valueLen > 8 && valueLen < 15;
    },

    onInputWhatsapp(ev) {
        this.orderUiState.whatsappButtonDisabled = false;
        this.orderUiState.inputWhatsapp = ev.target.value;
    },

    async onSendWhatsapp() {
        if (this.orderUiState.isSending) return;
        if (!this.is_valid_mobile()) {
            this.showPopup('ErrorPopup', {
                title: 'Invalid number',
                body: 'Please enter a valid phone number with country code (no +).',
            });
            return;
        }
        this.orderUiState.isSending = true;
        try {
            const ticketImage = await this.generateTicketImage();
            const number = this.orderUiState.inputWhatsapp;
            const message = this.orderUiState.inputMessage;
            await this.pos.data.call('pos.order', 'whatsapp_template_message', [number, message, ticketImage]);
            this.showPopup('ConfirmPopup', {
                title: 'Sent',
                body: 'Receipt sent via WhatsApp successfully!',
            });
        } catch (err) {
            console.error(err);
            this.orderUiState.whatsappButtonDisabled = true;
            this.showPopup('ErrorPopup', {
                title: 'Error',
                body: 'Failed to send WhatsApp message. Check logs and configuration.',
            });
        } finally {
            this.orderUiState.isSending = false;
        }
    },
});
