odoo.define('pos_home_delivery.pos_delivery', function (require) {
    "use strict";

    var Model = require('web.DataModel');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var _t = core._t;
    var gui = require('point_of_sale.gui');
    var PopupWidget = require('point_of_sale.popups');
    var models = require('point_of_sale.models');
    var OrderWidget = screens.OrderWidget;

    //  load employee as delivery person
    models.load_models({
    model: 'hr.employee',
    fields: ['name'],
        loaded: function(self, executives){
            self.executives = executives;
            var pos_executives = [];
            for (var i = 0; i < executives.length; i++) {
                var sale_person = executives[i];
                pos_executives.push(sale_person);
                self.executives = pos_executives;
            }
        },
    });

    // home delivery pop-up
    var DeliveryOrderWidget = PopupWidget.extend({
        template: 'DeliveryOrderWidget',
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },
        events: {
            'click .button.clear': 'click_clear',
            'click .button.cancel': 'click_cancel',
            'click .button.create': 'click_create',

        },
        show: function(options){
            this._super(options);
            this.renderElement();
            this.$('.d_name').focus();
        },
        
        //
        renderElement: function() {
            var self = this;
            this._super();
            var order = this.pos.get_order();
            this.$('.delivery-detail').hide();
            this.$('#apply_shipping_address').click(function() {
            	//console.log("applyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy");
            	if ($('#apply_shipping_address').is(':checked')) {
                    $('.delivery-detail').show();
                } else {
                    $('.delivery-detail').hide();
                }
            });
        },    
            
        get_orderline_data: function() {
            var order = this.pos.get_order();
            var orderlines = order.orderlines.models;
            var all_lines = [];
            for (var i = 0; i < orderlines.length; i++) {
                var line = orderlines[i]
                if (line && line.product && line.quantity !== undefined) {
                    all_lines.push({
                        'product_id': line.product.id,
                        'qty': line.quantity,
                        'price': line.get_display_price(),
                        'note': line.get_note(),
                    })
                }
            }
            return all_lines
        },
        click_create: function(){ 
            var self = this;
            var order = this.pos.get_order();
            var order_lines = self.get_orderline_data()
            if(order_lines.length > 0){
                var fields = {};
                this.$('.detail').each(function(idx, el){
                    fields[el.name] = el.value || false;
                });
                order.set_delivery_data(fields);
                var d_date = new Date(fields.delivery_date);
                fields.delivery_date = d_date.toISOString();
                /*
                var empty = $(".body").find('input[required], select[required]').filter(function() {
                    return this.value == '';
                  });
                if (empty.length){
                    self.gui.show_popup('error',{
                        'title': _t('Missing required'),
                        'body': _t('Some require details are missing OR you forget to give time in delivery date'),
                    });
                    return false;
                }
                */
                var order_date = new Date().toISOString();
                var order_data = {
                        'order_no' : order.name || order.uid || false,
                        'session_id': order.pos.pos_session.id || order.pos_session_id,
                        'order_date': order_date || false,
                        'cashier_id' : order.pos.user.id || false,
                }

                var partner = order.get_client();
                var orderlines = self.get_orderline_data();
                var date_delivery = $('.d_date').val();
                var notes = $('.order_note').val();
                var delivery_person = $('.person_id').val(); 
                
                var result = {
                    'form_data': fields,
                    'order_data': order_data,
                    'line_data' : order_lines,
                    'partner': partner
                }

                //
                if ($('#apply_shipping_address').is(':checked')) {
                    
		            new Model('pos.delivery.order').call('delivery_order_from_ui',[result]).then(function(data){return data;},function(err,event){
		                event.preventDefault();
		                self.gui.show_popup('error',{
		                    'title': _t('Delivery Order not Created'),
		                    'body': _t('Please fill your details properly.'),
		                });
		                return false;
		            });
                    
                    
                } else {

		            if(!delivery_person){
		                self.gui.show_popup('error',{
	                        'title': _t('Delivery Order not Created'),
	                        'body': _t('Please Assign a Delivery Person'),
	                    });  
		            }else{
		            new Model('pos.delivery.order').call('delivery_order_from_ui_with_partner',[ partner, order_data, orderlines, date_delivery, notes, delivery_person ]).then(function(data){return data;},function(err,event){
		                event.preventDefault();
		                self.gui.show_popup('error',{
		                    'title': _t('Delivery Order not Created'),
		                    'body': _t('Please fill your details properly.'),
		                });
		                return false;
		            });
		            
		            order.set_delivery_status(true);
                    if (order.delivery){
                        alert('Delivery order successfully created');
                    }
                    this.gui.close_popup();
		            
		            }
		            
		            
                }

                /*order.set_delivery_status(true);
                if (order.delivery){
                    alert('Delivery order successfully created');
                }
                this.gui.close_popup();*/
            }
            
        },
        click_clear: function(){
            this.$('.detail').val('');
            this.$('.d_name').focus();
        },
        click_cancel: function(){
            this.gui.close_popup();
            if (this.options.cancel) {
                this.options.cancel.call(this);
             }
        },
    });
    gui.define_popup({name:'delivery_order', widget: DeliveryOrderWidget});

    //  home delivery button on order
    var HomeDelivery = screens.ActionButtonWidget.extend({
        template: 'HomeDelivery',
        button_click: function(){
            var self = this;
            var order = this.pos.get_order();
            
            var partner_id = false
            if (order.get_client() != null)
                partner_id = order.get_client();

            if (!partner_id) {
                self.gui.show_popup('error', {
                    'title': _t('Unknown customer'),
                    'body': _t('You cannot use Home Delivery. Select customer first.'),
                });
                return;
            }                
                    
            var orderlines = order.orderlines.models;
            if(orderlines.length < 1){
                self.gui.show_popup('error',{
                        'title': _t('Empty Order !'),
                        'body': _t('Please select some products'),
                    });
                return false;
            }
            this.gui.show_popup('delivery_order',{
                'title': _t('Home Delivery Order'),
                'name' : order.get_div_name(),
                'email' : order.get_div_email(),
                'mobile' : order.get_div_mobile(),
                'address' : order.get_div_location(),
                'street' : order.get_div_street(),
                'city' : order.get_div_city(),
                'zip' : order.get_div_zip(),
                'delivery_date' : order.get_delivery_date(),
                'person_id' : order.get_div_person(),
                'order_note' : order.get_div_note(),
            });
        },
    });

    screens.define_action_button({
        'name': 'home_delivery',
        'widget': HomeDelivery,
        'condition': function () {
            return this.pos.config.pos_verify_delivery;
        },
    });

    // save delivery data into order
    var posorder_super = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attr, options) {
            posorder_super.initialize.call(this,attr,options);
            this.d_name = this.d_name || "";
            this.mobile = this.mobile || "";
            this.email = this.email || "";
            this.address = this.address || "";
            this.street = this.street || "";
            this.city = this.city || "";
            this.zip = this.zip || "";
            this.delivery_date = this.delivery_date || "";
            this.person_id = this.person_id || "";
            this.order_note = this.order_note || "";
            this.delivery = this.delivery || false;
        },
        set_delivery_data: function(fields){
            this.d_name = fields.d_name;
            this.mobile = fields.mobile;
            this.email = fields.email;
            this.address = fields.address;
            this.street = fields.street;
            this.city = fields.city;
            this.zip = fields.zip || "";
            this.delivery_date = fields.delivery_date;
            this.person_id = fields.person_id;
            this.order_note = fields.order_note;
            this.trigger('change',this);
        },
        set_delivery_status: function(delivery){
            this.delivery = delivery || true;
            this.trigger('change',this);
        },
        get_delivery_status: function(delivery){
            return this.delivery;
        },
        get_div_name:function(d_name){
            return this.d_name;
        },
        get_div_email:function(email){
            return this.email;
        },
        get_div_mobile:function(mobile){
            return this.mobile;
        },
        get_div_location:function(address){
            return this.address;
        },
        get_div_street:function(street){
            return this.street;
        },
        get_div_city:function(city){
            return this.city;
        },
        get_div_zip:function(zip){
            return this.zip;
        },
        get_delivery_date:function(delivery_date){
            return this.delivery_date;
        },
        get_div_person:function(person_id){
            return this.person_id;
        },
        get_div_note:function(order_note){
            return this.order_note;
        },
        export_as_JSON: function() {
            var json = posorder_super.export_as_JSON.apply(this,arguments);
            json.d_name = this.get_div_name();
            json.email = this.get_div_email();
            json.mobile = this.get_div_mobile();
            json.address = this.get_div_location();
            json.street = this.get_div_street();
            json.city = this.get_div_city();
            json.zip = this.get_div_zip();
            json.delivery_date = this.get_delivery_date();
            json.person_id = this.get_div_person();
            json.order_note = this.get_div_note();
            json.delivery = this.get_delivery_status();
            return json;
        },
        init_from_JSON: function(json){
            posorder_super.init_from_JSON.apply(this,arguments);
            this.set_delivery_data(json);
            this.delivery = json.delivery;
        },
    });

});
