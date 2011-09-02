(function($) {
	
	
	//var notify_tpl = 
	var notify = function notify(level,msg) {
		$('.container').prepend((new NotifyView({model:{level:level,message:msg}})).render().el)
	}
	

    var rotate = function rotate(degree,plus,$elie) {        
        $elie.css({ WebkitTransform: 'rotate(' + degree + 'deg)'});  
        $elie.css({ '-moz-transform': 'rotate(' + degree + 'deg)'});
        if (!$elie.get(0).stop_rotating) {
   	     	timer = setTimeout(function() {
	            rotate(degree+plus,plus,$elie);
	        },5);
			console.log('still rotating...')
		}
    }

	var stop_rotate = function stop_rotate($elie) {
		$elie.get(0).stop_rotating = true
        $elie.css({ WebkitTransform: 'rotate(0 deg)'});  
        $elie.css({ '-moz-transform': 'rotate(0 deg)'});
	}

	
	var NotifyView = window.NotifyView = Backbone.View.extend({
		
		className:'alert-message',
		
		events: {
			'click .alert-message .close': "countdown",
		},
		render:function() {
			$el = $(this.el).addClass(this.model.level)
			$el.html(_.template($('#notify-tpl').html(),this.model))
			this.countdown()
			return this
		},
		countdown:function() {
			var self = this
			setTimeout(function() {self.clear()},5000)
		},
		clear:function() {
			var self = this;
			$(this.el).fadeOut(self.remove)
		}
	})
	
	
	/* Models */
	var File = window.File = Backbone.Model.extend({
		defaults: {
			size:0,
			pid:null,
			icon:'/static/img/file.png',
			x:0,
			y:0,
			pub:false,
		},
		initialize: function() {
			this.bind('change', function(model,collection) {
				var prevattrs = model.previousAttributes()
				//console.log(model.changedAttributes())
				console.log('Saving File model: '+this.id)
				var self = this
				self.trigger('startworking')
				model.save({},{
					success:function(model,response) {
						if (self.content_to_upload) {
							self.content_to_upload.url = model.url()+'/content'
							self.content_to_upload.submit()
							console.log('Uploading file data!')
							self.content_to_upload = null;
						}
						self.trigger('stopworking')
						self.trigger('savesuccess')
					},
					error:function(model,response) {
						self.trigger('stopworking')
						self.trigger('saveerror',prevattrs)
						self.set(prevattrs,{silent:true})
					}
				});
				
			}, this);
		},
		download_url: function() {
			return this.url() + '/content'
		},
		delete: function() {
			var self = this;
			this.trigger('startworking')
			var stopwork = function() { self.trigger('stopworking')}
			this.destroy({success:stopwork,error:stopwork})
		},
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
			'click .file-view .delete': "dodelete",
		},
		
		className:'file-view',
		
		initialize: function() {
			var model = this.model
			var $el = $(this.el)
			this.el.view = this; // Add a reference to this view to this element
			
			// Bind the view elem for draggability
			$el.draggable({ containment: 'parent', opacity: .75 });
			//$el.bind('dragstop',function(e,ui) {
			//	model.set({x:ui.position.left, y:ui.position.top})
			//})
			
			//this.model.bind('change', this.render, this) // maybe?
			this.model.bind('destroy', this.doremove, this)
			this.model.bind('uploadprogress', this.updateprogress, this)
			this.model.bind('startworking', this.startworking, this)
			this.model.bind('stopworking', this.stopworking, this)
			this.model.bind('savesuccess', this.savesuccess, this)
			this.model.bind('saveerror', this.saveerror, this)
		},
		
		startworking:function() {
			$(this.el).addClass('working')
		},
		
		stopworking:function() {
			$(this.el).removeClass('working')
		},
		
		savesuccess:function() {
			$(this.el).effect("shake", { times:2, direction:'up', distance:5}, 100);
		},
		
		saveerror:function(prevattrs) {
			$el = $(this.el)
			left = $el.position().left;
			top = $el.position().top
			notify('error','There was an error saving your changes!')
			$(this.el).effect("shake", { times:2, direction:'left', distance:5}, 100)
				.fadeOut()
				.animate({left:prevattrs.x,top:prevattrs.y}, 80)
				.fadeIn()
		},
		
		updateprogress: function(percent) {
			console.log('Upload progress: '+ percent)
			$pbar = $(this.el).find('.progressbar')
			if (percent >= 100) {
				$pbar.hide()
				notify('info','File upload successful!')
			} else {
				$pbar.progressbar({value:percent})
				$pbar.show()
			}
		},
		
		download: function() {
			console.log('Download!')
			window.open(this.model.download_url())
		},
		
		doremove: function() {
			$this_el = $(this.el)
			var self = this
			rotate(0,10,$this_el)
			$this_el.hide("scale", {}, 1000, function() {
				//console.log('hidden')
				stop_rotate($this_el)
				self.remove()
				notify('info','File deleted!')
			});
		},
		
		dodelete: function() {
			this.model.delete();
		},
		
		render: function() {
			c = _.template($('#file-tpl').html())
			var $el = $(this.el)
			$el.css('position','absolute')
			$el.css('left',this.model.get('x'))
			$el.css('top',this.model.get('y'))
			tpl_vals = this.model.toJSON()
			tpl_vals.ext || (tpl_vals.ext = '')
			$el.html(c(tpl_vals))
			return this;
		}
	});
	

	var PileView = window.PileView = Backbone.View.extend({
			
		className:'pile-view',
			
		initialize: function() {
			this.counter = 0;
			//this.model.files.bind('add', this.rebinddroppables, this);
			//this.model.files.bind('all', console.log, this);
			var $el = $(this.el),
				file_collection_selector = '.file-collection',
				self = this
			
			// Setup fileuploader
			$el.fileupload({
				add:function(e, data) {
					_.each(data.files, function (file) {
						var filename = file.name || file.fileName;
						var namearray = filename.split('.'),
						 	ext = namearray.length>1 ? _.last(namearray) : '';
							x = e.pageX - $el.find(file_collection_selector).offset().left
							y = e.pageY = $el.find(file_collection_selector).offset().top
						
						f = new File({
							x:x,
							y:y,
							name:filename,
							size:file.size,
							type:file.type,
							ext:ext
						});
						data.associated_file_model = f
						f.content_to_upload = data
						self.add(f);
						f.save()
					});
				},
				progress: function(e, data) {
					data.associated_file_model.trigger('uploadprogress',parseInt(data.loaded / data.total * 100))
				},
				url:"BAD_URL",//this.model.files.url,
				type:'PUT',
				//dropZone:$el, <--- So actually we probably want to do the whole document
				send:function(e, data) {
				},
				start:function(e) {
				}
			})
			
			this.render();
			
			this.rebinddroppables()
		},
		
		rebinddroppables:function() {
			console.log('rebind-droppables')
			$el = $(this.el)
			$el.find('.trash').droppable({
				drop:function(e,ui) {
					ui.draggable[0].view.dodelete() // Thats kinda hacky...
					//ui.draggable[0].view.model.set({x:ui.position.left, y:ui.position.top})
				},
				tolerance:'fit',
				hoverClass:'drophover',
				greedy:true,
			});
			$el.find('.private').droppable({
				drop:function(e,ui) {
					elem = ui.draggable[0]
					elem.view.model.set({pub:false, x:ui.position.left, y:ui.position.top})
				},
				tolerance:'intersect',
				hoverClass:'drophover',
				greedy:true,
			});
			$el.find('.public').droppable({
				drop:function(e,ui) {
					elem = ui.draggable[0]
					elem.view.model.set({pub:true, x:ui.position.left, y:ui.position.top})
				},
				tolerance:'intersect',
				hoverClass:'drophover',
				greedy:true,
			});
		},
		
		render: function() {
			$this_el = $(this.el)
			$this_el.html('')
			var $pile_elems = $(_.template($('#pile-tpl').html(), this.model.toJSON()))
			// Build fileviews
			$this_el.html($pile_elems)
			var $collection = $this_el.find('.file-collection')
			var fileviews = _.map(this.model.files.models,function(m) {
				return new FileView({model:m})
			})
			_.each(fileviews,function(fileview) { 
				$collection.append(fileview.render().el)
			})
			
			this.rebinddroppables()
			
			return this;
		},
		
		add: function(file_model) {
			this.counter += 1;
			this.model.files.add(file_model)
			this.render();
		},
		
	});
	
	
})(jQuery)
