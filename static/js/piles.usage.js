$(function() {
	
	var Usage = Backbone.Model.extend({
		defaults: {
			
		},
	});
	
	var UsageView = Backbone.View.extend({
		
		className: '',
		
		initialize: function() {
			
		},
		animate_progressbar: function($pbar,to) {
			var step_pbar = function($pbar,at,to) {
				$pbar.progressbar( "option", "value",at)
				if (at < to) {
					setTimeout(function() {step_pbar($pbar,at+1,to)}, 15);
				}
			}
			step_pbar($pbar,0,to)
		},
		render:function() {
			$(this.el).html($('#usage-tpl').html(),this.model.toJSON())
			return this
		}
	});
});