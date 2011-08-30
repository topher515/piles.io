(function($) {
	
	
	/* Models */
	var File = window.File = Backbone.Model.extend({
		defaults: {
			size:0,
			pid:null,
			icon:'/static/img/file.png',
			x:0,
			y:0,
		},
		initialize: function() {
			this.bind('change', function() {
				console.log('Saving File model: '+this.id)
				var self = this
				this.save({},{success:function(model,response) {
					if (self.content_to_upload) {
						self.content_to_upload.url = model.url()+'/content'
						self.content_to_upload.submit()
						console.log('Uploading file data!')
						self.content_to_upload = null;
					}
				}});
				
			}, this)
		},
		download_url: function() {
			return this.url() + '/content'
		}
	});
	
	var FileCollection = window.FileCollection = Backbone.Collection.extend({
		model: File,
	})
	
	var Pile = window.Pile = Backbone.Model.extend({
		urlRoot: '/piles',
		initialize: function() {
			this.files = new FileCollection,
			this.files.url = '/piles/'+this.id+'/files'
		},
	});

	/* Views */
	var FileView = window.FileView = Backbone.View.extend({
		
		events: {
			'dblclick .file-view .download':	"download",
			'click .file-view .delete': "delete",
		},
		
		className:'file-view',
		
		initialize: function() {
			var model = this.model
			var $el = $(this.el)
			
			// Bind the view elem for draggability
			$el.draggable();
			$el.bind('dragstop',function(e,ui) {
				model.set({x:ui.position.left, y:ui.position.top})
			})
			
			//this.model.bind('change', this.render, this) // maybe?
			this.model.bind('destroy', this.remove, this)
		},
		
		download: function() {
			console.log('Download!')
			window.open(this.model.download_url())
		},
		
		delete: function() {
			this.model.destroy();
		},
		
		render: function() {
			c = _.template($('#file-tpl').html())
			var $el = $(this.el)
			$el.css('left',this.model.get('x'))
			$el.css('top',this.model.get('y'))
			$el.html(c(this.model.toJSON()))
			return this;
		}
	});
	

	var PileView = window.PileView = Backbone.View.extend({
			
		className:'pile-view',
			
		initialize: function() {
			this.counter = 0;
			//this.model.files.bind('add', this.add, this);
			//this.model.files.bind('all', console.log, this);
			$el = $(this.el)
			self = this
			
			// Setup fileuploader
			$el.fileupload({
				add:function(e, data) {
					_.each(data.files, function (file) {
						
						f = new File({x:e.pageX,y:e.pageY,name:file.name});
						f.content_to_upload = data
						self.add(f);
					});
				},
				url:"BAD_URL",//this.model.files.url,
				type:'PUT',
				send:function(e, data) {
				},
				start:function(e) {
				}
			})
			
			this.render();
		},
		
		render: function() {
			$this_el = $(this.el)
			$this_el.html('')
			var h = _.template("<span><%= emails %></span>", this.model.toJSON())
			var fileviews = _.map(this.model.files.models,function(j) { 
				return new FileView({model:j}); 
			})
			_.each(fileviews, function(i) {
				i.render()
				$this_el.append(i.el)	
			})
			$this_el.append(h)
			return this;
		},
		
		add: function(file_model) {
			this.counter += 1;
			this.model.files.add(file_model)
			this.render();
		},
		
	});
	
	
	
})(jQuery)
