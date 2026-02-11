Meta WhatsApp Business API Integration for Odoo 18
A comprehensive WhatsApp Business API integration module for Odoo 18 using Meta’s official WhatsApp Business API.

Features
✅ Meta WhatsApp Business API Integration - Official API support
✅ Multiple Business Accounts - Support for multiple WhatsApp Business accounts
✅ Template Messages - Pre-approved message templates with parameters
✅ Contact Management - WhatsApp numbers and opt-in management
✅ POS Integration - Send receipts directly from Point of Sale
✅ Message History - Complete message tracking and history
✅ Webhook Support - Receive delivery status and incoming messages
✅ Multi-language Templates - Support for multiple languages
Requirements
Meta WhatsApp Business API Setup
WhatsApp Business Account - Active WhatsApp Business account
Meta Business Account - Facebook/Meta Business account
WhatsApp Business API Access - Approved API access
Phone Number - Verified business phone number
Odoo Requirements
Odoo 18.0+
base, mail, contacts, point_of_sale modules
Installation
Copy the module to your Odoo addons directory:

cp -r meta_whatsapp_integration /path/to/odoo/addons/
Update the apps list in Odoo:

Go to Apps → Update Apps List
Install the module:

Search for “Meta WhatsApp Business API Integration”
Click Install
Configuration
Step 1: Get Meta API Credentials
Create Meta Business Account

Go to business.facebook.com
Create or use existing business account
Set up WhatsApp Business API

Go to developers.facebook.com
Create a new app or use existing
Add WhatsApp Business product
Complete business verification
Get Required Information

Phone Number ID: From WhatsApp → API Setup
Access Token: Generate permanent access token
Business Account ID: From WhatsApp → API Setup
Webhook Verify Token: Create your own secure token
Step 2: Configure in Odoo
Create Business Account

Go to WhatsApp → Configuration → Business Accounts
Click Create
Fill in the Meta API credentials:
Name: Your account name
Phone Number ID: From Meta
Access Token: Permanent token from Meta
Business Account ID: From Meta
Webhook Verify Token: Your secure token
Test Connection

Click “Test Connection” button
Verify status shows “Connected”
Set as default if needed
Set up Templates (Optional)

Go to WhatsApp → Configuration → Message Templates
Create templates for common messages
Templates need Meta approval before use
Usage
Sending Messages
From Contact Records
Open any contact (Customers)
Add WhatsApp number in the contact form
Enable “WhatsApp Opt-in”
Click “Send WhatsApp” button
Choose message type (Text or Template)
Send message
From WhatsApp Menu
Go to WhatsApp → Send Message
Select business account
Enter recipient details
Compose and send message
POS Integration
Send Receipt via WhatsApp
Complete a POS order with customer
Ensure customer has WhatsApp number
Click “Send WhatsApp Receipt” in POS
Choose receipt format
Send receipt
Message Templates
Creating Templates
Go to WhatsApp → Configuration → Message Templates
Click Create
Fill template details:
Name: Template identifier
Category: UTILITY, MARKETING, or AUTHENTICATION
Language: Template language
Content: Header, body, footer text
Parameters: Use {{1}}, {{2}}, etc. for variables
Template Approval
Templates must be approved by Meta before use
Submit templates through Meta Business Manager
Status will update automatically via API
API Endpoints
Webhook Configuration (Optional)
Set up webhook in Meta Business Manager:

Webhook URL: https://yourdomain.com/whatsapp/webhook
Verify Token: Your webhook verify token
Subscribed Fields: messages, message_deliveries
Troubleshooting
Common Issues
Connection Failed

Verify API credentials are correct
Check access token permissions
Ensure phone number is verified
Message Send Failed

Check recipient number format (+country_code)
Verify customer opt-in status
Check template approval status
Template Not Working

Ensure template is approved by Meta
Check parameter count matches
Verify template name spelling
Error Codes
100: Invalid parameter
131000: Generic user error
131016: Message undeliverable
131021: Recipient not reachable
131026: Message expired
131047: Re-engagement message
131051: Unsupported message type
Security
Store access tokens securely
Use HTTPS for webhook endpoints
Validate webhook signatures
Implement rate limiting
Regular token rotation
Support
Documentation
Meta WhatsApp Business API Docs
WhatsApp Business Platform
Getting Help
Check Odoo logs for detailed errors
Verify Meta API status
Test with Meta API testing tools
License
LGPL-3 License

Changelog
Version 18.0.1.0.0
Initial release
Meta WhatsApp Business API integration
Template message support
POS receipt integration
Contact management
Message history tracking