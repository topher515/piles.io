(function($) {
	
	var get_icon = window.get_icon = function(ext) {
		var img_icons = {
			aac:'aac_icon.png',
			ai:'ai_icon.png',
			avi:'avi_icon.png',
			css:'css_icon.png',
			doc:'doc_icon.png',
			docx:'docx_icon.png',
			gif:'gif_icon.png',
			gzip:'gzip_icon.png',
			gz:'gzip_icon.png',
			html:'html_icon.png',
			jpeg:'jpeg_icon.png',
			jpg:'jpg_icon.png',
			js:'js_icon.png',
			ma:'ma_icon.png',
			mov:'mov_icon.png',
			mp:'mp_icon.png',
			mpeg2:'mpeg_icon.png',
			mp3:'mp3_icon.png',
			mp2:'mpeg_icon.png',
			mpg:'mpg_icon.png',
			mv:'mv_icon.png',
			pdf:'pdf_icon.png',
			php:'php_icon.png',
			php3:'php_icon.png',
			png:'png_icon.png',
			psd:'psd_icon.png',
			raw:'raw_icon.png',
			rtf:'rtf_icon.png',
			tar:'tar_icon.png',
			tiff:'tiff_icon.png',
			wav:'wav_icon.png',
			wmv:'wmv_icon.png',
			zip:'zip_icon.png',
		}
		if (img_icons[ext]) return '/static/img/icons/' + img_icons[ext]
		return '/static/img/file.png'
	}
	
	/* Utilities */
	var rotate = function rotate(degree,plus,$elie) {        
        $elie.css({ WebkitTransform: 'rotate(' + degree + 'deg)'});  
        $elie.css({ '-moz-transform': 'rotate(' + degree + 'deg)'});
        if (!$elie || !$elie.get(0).stop_rotating) {
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
	
	window.human_size = function human_size(num) {
		var sizes = ['bytes','KB','MB','GB','TB']
		for (x in sizes) {
			if (num < 1024.0) {
				return '' + num.toFixed(2) + ' '+ sizes[x]
			}
			num = num/ 1024.0 
		}
	}
	
	/* Global Helpers */
	var notify = function notify(level,msg) {
		$('.container').prepend((new NotifyView({model:{level:level,message:msg}})).render().el)
	}
	
	var ModalFileView = window.ModalFileView = Backbone.View.extend({
		className:'modal modal-file-view',
		events: {
			'click .modal-file-view .close': "clear",
		},
		initialize: function() {
			var self = this;
			$('.blockUI').click(self.clear)
		},
		render:function() {
			var $el = $(this.el),
				tpl = _.template($('#modal-tpl').html()),
				attrs = this.model.toJSON()
			$el.html(tpl(attrs))
			//$el.dialog({modal:true})
			return this
		},
		countdown:function() {
			var self = this
			setTimeout(function() {self.clear()},5000)
		},
		clear:function() {
			var self = this;
			$.unblockUI()
			$(this.el).fadeOut(self.remove)
		}
	});


	var NotifyView = window.NotifyView = Backbone.View.extend({
		
		className:'alert-message',
		
		events: {
			'click .alert-message .close': "clear",
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
				var prevattrs = model.previousAttributes(),
					self = this,
					attrs = model.attributes
				console.log('Saving File model: '+this.id)
				self.trigger('startworking')
				model.save({},{
					success:function(model,response) {
						if (self.content_to_upload) {
							self.content_to_upload.url = model.url()+'/content'
							self.content_to_upload.submit()
							self.trigger('startworking')
							console.log('Uploading file data!')
							self.content_to_upload = null;
						} else {
							self.trigger('stopworking')
							self.trigger('savesuccess',attrs)
						}
					},
					error:function(model,response) {
						self.trigger('stopworking')
						self.trigger('saveerror',prevattrs)
						// Reset the model to BEFORE the save
						// TODO: Get rid of this major hack that breaks OO
						// HACK
						for (var attr in prevattrs) {
							self.attributes[attr] = prevattrs[attr]
						}
						self._previousAttributes = prevattrs
						// ENDHACK
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
		defaults:{
			welcome:false,
		},
		initialize: function() {
			this.files = new FileCollection
			this.files.url = '/piles/'+this.id+'/files'
			var self = this;
			this.bind('change',function(model) {
				var new_name = model.hasChanged('name')
				model.save({},{success: function() {
					if (new_name) self.trigger('renamesuccess')
				}});
			});
		},
		validate: function(attrs) {
			if (attrs.name == '') {
				return "Name can't be blank";
			}
		},
	});

	/* Views */
	var FileView = window.FileView = Backbone.View.extend({
		
		events: {
			'dblclick .file-view .icon-display': "download",
			'click .file-view .delete': "dodelete",
			'click .file-view .info': 'domodal',
		},
		
		className:'file-view',
		
		initialize: function() {
			var model = this.model,
				$el = $(this.el),
				self = this;
			this.el.view = this; // Add a reference to this view to this element
			
			// Bind the view elem for draggability
			$el.draggable({
				containment: 'parent', 
				opacity: .75,
				start: function(e,ui) {
					$el.animate({width:$el.prev_width, height:$el.prev_height})
				}
			});
		
			if (this.model.get('pub')) $el.addClass('pub')
			
			/* Hover animations */
			$el.hover(
				function() {
					if ($el.hasClass('working')) return
					if (!$el.prev_height) {
						$el.prev_height = $el.height()
						$el.prev_width = $el.width()
					}
					if (!$el.auto_height) {
						$el.css({height:'auto'}) // ,width:'auto'})  <--- Let's not set the width as an experiment
						$el.auto_height = $el.height()
						$el.auto_width = $el.width()
						$el.css({height:$el.prev_height,width:$el.prev_width})
					}
					$el.animate({height:$el.auto_height,width:$el.auto_width})
				},
				function() {
					if ($el.hasClass('working')) return
					$el.animate({height:$el.prev_height,width:$el.prev_width})
				}
			)
			
			this.model.bind('destroy', this.doremove, this)
			this.model.bind('uploadprogress', this.updateprogress, this)
			this.model.bind('uploadsuccess', this.uploadsuccess, this)
			this.model.bind('startworking', this.startworking, this)
			this.model.bind('stopworking', this.stopworking, this)
			this.model.bind('savesuccess', this.savesuccess, this)
			this.model.bind('saveerror', this.saveerror, this)
		},
		
		domodal:function() {
			$.blockUI({
				message: new ModalFileView({model:this.model}).render().el,
				css: {cursor:'auto'}
			})
			//$(".blockMsg").hide() // Hack
			//$('.container').append()
		},
		
		startworking:function() {
			$(this.el).addClass('working').draggable('option','disabled',true)
		},
		
		stopworking:function() {
			$(this.el).removeClass('working').draggable('option','disabled',false)
		},
		
		savesuccess:function(attrs) {
			var $el = $(this.el);
			attrs.pub ? $el.addClass('pub') : $el.removeClass('pub');
			$el.effect("shake", { times:2, direction:'up', distance:5}, 100);
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
			if (percent <= 100) {
				$pbar.progressbar({value:percent})
				$pbar.show()
			}
		},
		
		uploadsuccess: function() {
			$pbar = $(this.el).find('.progressbar').hide('slide',{direction:"right"})
			this.stopworking()
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
		
		events:{
			'click .pile-view .rename': 'dorename',
		},
			
		initialize: function() {
			this.counter = 0;
			//this.model.files.bind('add', this.rebinddroppables, this);
			//this.model.files.bind('all', console.log, this);
			var $el = $(this.el),
				file_collection_selector = '.file-collection',
				self = this;
			
			/* Handle EMPTY */
			if (this.model.files.models.length == 0) {
				$el.addClass('empty')
			} else {
				$el.removeClass('empty')
			}
			
			/* Setup bindings */
			this.model.files.bind('add', function() {
				$el.removeClass('empty')
			});
			this.model.files.bind('remove', function() {
				if (self.model.files.models.length == 0) {
					$el.addClass('empty')	
				}
			});
			
			/* Handle renames */
			this.model.bind('renamesuccess', this.renamedone, this);
			/* Check for usage change on remove */
			self.model.files.bind('remove',function() {self.model.fetch() })
			/* Handle usage changes */
			this.model.bind('change:usage_put',this.updateusage,this)
			this.model.bind('change:usage_get',this.updateusage,this)
			this.model.bind('change:usage_sto',this.updateusage,this)
			
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
				},
				done:function(e, data) {
					notify('info','File upload successful!')
					data.associated_file_model.trigger('uploadsuccess')
					// Grab new usage stats
					self.model.fetch()
				}
			})
			
			this.render();
			
			this.rebinddroppables()
			
			if (this.model.get('welcome')) {
				notify('info','<strong>Hi! Welcome to Piles</strong>—Where our philosophy is, "Put on some pants for god sakes."')
				this.model.set({'welcome':false})
			}
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
		
		updateusage: function() {
			var $el = $(this.el)
			$el.find('.usage .usage-up').html(human_size(this.model.get('usage_put')))
			$el.find('.usage .usage-down').html(human_size(this.model.get('usage_get')))
			$el.find('.usage .usage-sto').html(human_size(this.model.get('usage_sto')))
		},
		
		dorename: function() {
			var newname = prompt('New name for your Pile',this.model.get('name'))
			this.model.set({'name':newname})
		},
		renamedone: function() {
			window.location.href = '/' + this.model.get('name')
			//$(this.el).find('.pile-name span').html(this.model.get('name'))
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
