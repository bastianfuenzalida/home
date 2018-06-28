# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'POS Home Delivery',
    'version': '10.0.0.4',
    'author': 'BrowseInfo',
    'sequence': 120,
    'category': 'Point of sale',
    'website': 'www.browseinfo.in',
    'summary': 'This apps helps to manage home delivery feature on POS with Delivery details',
    'description': """ Create home delivery in point of sale
	Point of Sale Home Delivery,
	Home Delivery on POS
	Home Delivery on Point of Sale
	Pos Pay Later 
	POs Pay after delivery
	POS Pay delivery, 
	Point of sale payment after delivery
	POS payment home delivery
	POS home delivery payment
	POS cash on delivery
	POS COD

""",
    'depends': ['hr', 'pos_restaurant'],
    'data': ['views/pos_delivery_template.xml', 'views/pos_delivery_view.xml', 'security/ir.model.access.csv'],
    'qweb': ['static/src/xml/pos_delivery.xml'],
    'installable': True,
    'application': True,
    'price': '49',
    'currency': "EUR",
    "images":["static/description/Banner.png"],
}
