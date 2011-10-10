%from settings import settings


<script>
$(function() {
	
	var Feedback = Backbone.Model.extend({
	    defaults:{
	        useragent:navigator.userAgent
	    },
		urlRoot:'http://{{settings("APP_DOMAIN")}}/feedbacks'
	});
	
	var FeedbackView = Backbone.View.extend({
		
		className:'modal feedback-widget',
		
		events:{
			'click .feedback-widget .close':'clear',
			'click .feedback-widget .bug':'dobug',
			'click .feedback-widget .like':'dolike',
			'click .feedback-widget .dislike':'dodislike',
			'click .feedback-widget input[type=submit]':'send',
		},
		
		render:function() {
			var tpl = _.template($('#feedback-tpl').html()),
				raw = tpl({}),
				$new_elem = $(raw);
			$new_elem.find('.feedback-more').hide()
			$(this.el).html($new_elem)				
			return this;
		},
		clear:function() {
			$.unblockUI()
			var self = this;
			$(this.el).fadeOut(self.remove)
		},
		dodislike:function() {
			var self = this,
				$el = $(self.el);
			$more = $el.find('.feedback-more').hide()
			$el.find('.dislike input[type=radio]').attr('checked','checked')
			$msg = $el.find('.message')
			$msg.find('.help-block').html('Let us know what you don\'t like. Hopefully we can make it better. Something like: <em>"Piles.io? More like Pile-o-sh*t! Am-I-rite?!?"</em>... but maybe more constructive.')
			$more.show('fadeIn')
		},
		dobug:function() {
			var self = this,
				$el = $(self.el);
			$more = $el.find('.feedback-more').hide()
			$el.find('.bug input[type=radio]').attr('checked','checked')
			$msg = $(self.el).find('.message')
			$msg.find('.help-block').html("Please try to leave a thorough description of what you were doing when you encountered the bug!")
			$more.show('fadeIn')
		},
		dolike:function() {
			var self = this,
				$el = $(self.el);
			$more = $el.find('.feedback-more').hide()
			$el.find('.like input[type=radio]').attr('checked','checked')
			$msg = $(self.el).find('.message')
			$msg.find('.help-block').html("We love positive feed back! Let us know what you like!")
			$more.show('fadeIn')
		},
		send:function() {
			this.model.set({
				message:$(this.el).find('.message textarea').val(),
				type:$(this.el).find('input[type=radio]:checked').val(),
				email:$(this.el).find('input[name=email]').val()
			})
			this.model.save()
			this.clear()
		},
	})
	
	$('.feedback-button').hover(
	    function() {
	        $(this).animate({left:0})
	    },
	    function() {
	        $(this).animate({left:-126})
	    }
	    ).click(function() {
	    	$.blockUI({
    			message: (new FeedbackView({model:new Feedback()})).render().el,
    			css: {cursor:'auto'}
    		})
    		$('body').append()
    	})
})
</script>

<style type="text/css" media="screen">
.feedback-button-container {
    position:fixed;
	left:0;
	top:35%;
	z-index:1000;
}
.feedback-button {
    position:absolute;
    left:-126px;
	width: 156px;
	height:22px;
	background: rgb(224,224,224); /* Old browsers */
    background: -moz-linear-gradient(top, rgba(224,224,224,1) 0%, rgba(197,197,197,1) 100%); /* FF3.6+ */
    background: -webkit-gradient(linear, left top, left bottom, color-stop(0%,rgba(224,224,224,1)), color-stop(100%,rgba(197,197,197,1))); /* Chrome,Safari4+ */
    background: -webkit-linear-gradient(top, rgba(224,224,224,1) 0%,rgba(197,197,197,1) 100%); /* Chrome10+,Safari5.1+ */
    background: -o-linear-gradient(top, rgba(224,224,224,1) 0%,rgba(197,197,197,1) 100%); /* Opera11.10+ */
    background: -ms-linear-gradient(top, rgba(224,224,224,1) 0%,rgba(197,197,197,1) 100%); /* IE10+ */
    filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#e0e0e0', endColorstr='#c5c5c5',GradientType=0 ); /* IE6-9 */
    background: linear-gradient(top, rgba(224,224,224,1) 0%,rgba(197,197,197,1) 100%); /* W3C */
    padding:5px;
    -webkit-border-top-right-radius: 5px;
    -webkit-border-bottom-right-radius: 5px;
    -moz-border-radius-topright: 5px;
    -moz-border-radius-bottomright: 5px;
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
    -webkit-box-shadow: 4px 4px 5px 0px , 0, 0, .5);
    -moz-box-shadow: 4px 4px 5px 0px , 0, 0, .5);
    box-shadow: 4px 4px 5px 0px , 0, 0, .5);
    cursor:pointer;
    }
    .feedback-button span {
        vertical-align:middle;
        margin-top:3px;
    }
    .feedback-button img {
        float:right;
    }

.feedback-widget {

	width: 500px;
	}
	.feedback-widget .feedback-type li {
		float:left;
		list-style:none;
		width: 140px;
	}
	.feedback-widget .feedback-type img {
		max-width: 128px;
	}
	.feedback-widget .message textarea {
		width: 280px;
		height: 80px;
	}
</style>

<div class="feedback-button-container">
    <div class="feedback-button">
    	<span>Feedback &amp; Support</span><img src="http://{{settings('CONTENT_DOMAIN')}}/static/img/speechbubble.png" />
    </div>
</div>

<script type="text/template" id="feedback-tpl">
	<div class="modal-header">
		<h3>
			Feedback &amp; Support
		</h3><a href="#" class="close">&times;</a>
	</div>
	<div class="modal-body">
	
	<form>
		<input type="hidden" name="current_url" value="<%= window.location.href %>">
		<div class="clearfix">
				<ul class="feedback-type">
					<li>
							<div class="dislike">
								<img src="http://{{settings('CONTENT_DOMAIN')}}/static/img/thumb_dislike_big.png">
								<span>
								<input type="radio" name="type" value="dislike"> This sucks!</span>
							</div>
					</li>
					<li>
							<div class="bug">
								<img src="http://{{settings('CONTENT_DOMAIN')}}/static/img/bug_big.png">
								<span>
								<input type="radio" name="type" value="bug"> Report a Bug</span>
							</div>
					</li>
					<li>
							<div class="like">
								<img src="http://{{settings('CONTENT_DOMAIN')}}/static/img/thumb_like_big.png">
								<span>
								<input type="radio" name="type" value="like"> This is awesome!</span>
							</div>
					</li>
				</ul>
		</div><!-- /clearfix -->
		<div class="clearfix feedback-more">
			<label for="feedback-email">Email</label>
			<div class="input">
				<input type="text" id="feedback-email" class="large" name="email"></input>
				<span class="help-block">Optional</span>
			</div>
			<label for="feedback-message">Message</label>
			<div class="message input">
				<textarea class="large" id="feedback-message" name="message"></textarea> 
				<span class="help-block">What's up? If you're reporting a bug, then please give a thorough description!</span>
			</div>
		</div><!-- /clearfix -->
		
	</form>
	</div>
	<div class="modal-footer">
			<input type="submit" class="btn primary" value="Send">&nbsp;<button type="reset" class="btn close">Cancel</button>
	</div>

</script>