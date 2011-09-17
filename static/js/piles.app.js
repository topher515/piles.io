(function($) {
	
	window.PilesIO ? console.log('PilesIO already in global scope') : window.PilesIO = {}
	
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
		if (img_icons[ext]) return '/static/img/icons/' + img_icons[ext.toLowerCase()]
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
	
	window.human_size = PilesIO.human_size = function(num) {
		var sizes = ['bytes','KB','MB','GB','TB']
		for (x in sizes) {
			if (num < 1024.0) {
				return '' + num.toFixed(2) + ' '+ sizes[x]
			}
			num = num/ 1024.0 
		}
	}
	
	window.insert_spacers = PilesIO.insert_spacers = function(string,len) {
	    if (!len) len = 10
	    cursor = 0
	    new_string = []
	    since_last_spacer = 0
	    while (cursor < string.length) {
	        c = string[cursor] 
	        if (c != ' ' && c != '\n' && c != '\t' && c != '-') {
	            since_last_spacer++;
	        } else {
	            since_last_spacer = 0
	        }   
	        new_string.push(c)
	        if (since_last_spacer > len) {
                new_string.push(' ')
                since_last_spacer = 0
            }
	        cursor++
	    }
	    n = new_string.join('')
	    return n;
	}
	
	// Helper function to get a URL from a Model or Collection as a property
    // or as a function. // From Backbone.js
    var getUrl = function(object) {
      if (!(object && object.url)) return null;
      return _.isFunction(object.url) ? object.url() : object.url;
    };

    // Throw an error when a URL is needed, and none is supplied. // From Backbone.js
    var urlError = function() {
      throw new Error('A "url" property or function must be specified');
    };
	
	/* Global Helpers */
	window.notify = function notify(level,msg) {
		$('body').prepend((new NotifyView({model:{level:level,message:msg}})).render().el)
	}
	
	PilesIO.App = {
	    AWS_BUCKET:'',
        FILE_POST_URL:'',
        AWS_ACCESS_KEY_ID:'',
        APP_DOMAIN:'',
    }
    
    /***************
     * Backbone overrides
     ***************/
     Backbone.sync = function(method, model, options) {
         var type = {
            'create': 'POST',
            'update': 'PUT',
            'delete': 'DELETE',
            'read'  : 'GET'
          }[method];

         // Default JSON-request options.
         var params = _.extend({
           type:         type,
           dataType:     'jsonp'
         }, options);

         // Ensure that we have a URL.
         if (!params.url) {
           params.url = getUrl(model) || urlError();
         }

         if (type != 'DELETE') {
             params.data = {model: JSON.stringify(model.toJSON())}
         } else {
             params.data = {}
         }
    
         // For JSONp emulate HTTP by mimicking the HTTP method with `_method`
         // And an `X-HTTP-Method-Override` header.
         if (type === 'PUT' || type === 'DELETE' || type === 'POST') {
             params.data._method = type;
             params.type = 'GET';
             params.beforeSend = function(xhr) {
               xhr.setRequestHeader('X-HTTP-Method-Override', type);
             };
         }

         // Make the request.
         return $.ajax(params);
    };
    
    
    /*************
     * Controllers 
     **************/
     /// FYI Currently most M<-->V communication is direct; only the complex fileupload functionality has a controller.

    var FileUploadController = function() {
        var filemodel_stack = [];
        
        this.get_form_data = function() {
            var filemodel_ = _.last(filemodel_stack)
            fdata = {
                AWSAccessKeyId: PilesIO.App.AWS_ACCESS_KEY_ID,
    		    acl: PilesIO.App.APP_BUCKET_ACL,
    		    key: filemodel_.get('path'),
    		    signature: filemodel_.get('signature'),
    		    policy: filemodel_.get('policy')
            }
            newfdata = []
            for (key in fdata) {
                newfdata.push({
                    name:key,
                    value:fdata[key]
                })
            }
            return newfdata;
        },
        
        this.setup_upload = function($fileuploader, filemodel, filedata) {
            
            //filemodel.filedata = filedata;
            //filedata.filemodel = filemodel;
            
            var savesuccesscallback = function(filemodel) {
                // Unbind this function so its not called when we save the file again in the future
                // e.g., when we move it around the pile
				filemodel.unbind('savesuccess',savesuccesscallback)
				// Start the file upload
                filemodel.trigger('startworking')
                filedata.url = PilesIO.App.FILE_POST_URL
                filedata.filemodel = filemodel
                filemodel_stack.push(filemodel)
                filedata.submit()
                filemodel_stack.pop()
            }
            
            var fileuploaddonecallback = function(e, data) {
                $fileuploader.unbind('fileuploaddone',fileuploaddonecallback)
				notify('info','File upload successful!')
				// Unbind model
				data.filemodel.trigger('uploadsuccess')
				data.filemodel.trigger('stopworking')
			}
			
			var fileuploadprogresscallback = function(e, data) {
                data.filemodel.trigger('uploadprogress',parseInt(data.loaded / data.total * 100))
            }
            
            var fileuploadfailcallback = function(e, data) {
			    data.filemodel.trigger('uploaderror', data)
			    data.filemodel.delete()
			}
            
            $fileuploader.bind('fileuploadprogress',fileuploadprogresscallback)
            $fileuploader.bind('fileuploaddone', fileuploaddonecallback)
			$fileuploader.bind('fileuploadfail', fileuploadfailcallback)
			filemodel.bind('savesuccess',savesuccesscallback)
        }
    }
    var file_upload_controller = new FileUploadController()
	

	/*************
	 * Models
	 **************/
	var File = PilesIO.File = Backbone.Model.extend({
		defaults: {
			size:0,
			pid:null,
			icon:'/static/img/file.png',
			x:0,
			y:0,
			pub:false,
			type:'Unknown File',
		},
		initialize: function() {
		    
		    // Reset to sane values
		    if (this.get('x') > 100) { this.set({'x':95}) }
		    else if (this.get('x') < 0) { this.set({'x':0}) }
		    
		    if (this.get('y') > 100) { this.set({'y':90}) }
		    else if (this.get('y') < 0) { this.set({'y':0}) }
		    
		    // Bind to file changes 
			this.bind('change', function(model,collection) {
				var prevattrs = model.previousAttributes(),
					self = this,
					attrs = model.attributes
					
				console.log('Saving File model: '+this.id)
				self.trigger('startworking')
				model.save({},{
					success:function(model,response) {
						/*if (self.content_to_upload) {
							self.content_to_upload.url = model.url()+'/content'
							self.content_to_upload.submit()
							self.trigger('startworking')
							console.log('Uploading file data!')
							self.content_to_upload = null;
						} else {*/
						self.trigger('stopworking')
						self.trigger('savesuccess',model)
						//}
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
						//self.set(prevattrs,{silent:true})
					}
				});
				
			}, this);
		},
		download_url: function() {
			return 'http://' + PilesIO.App.APP_DOMAIN + '/piles/' + this.get('pid') + '/files/' + this.get('id') + '/content'
		},
		delete: function() {
			var self = this;
			this.trigger('startworking')
			this.destroy({
			    success:function() { 
			        self.trigger('stopworking')
			    },
			    error:function() {
			        notify('error','Failed to delete file.')
			    }
		    });
		},
	});
	
	var FileCollection = PilesIO.FileCollection = Backbone.Collection.extend({
		model: File,
	});
	
	var Daily = PilesIO.Daily = Backbone.Model.extend({
        initialize:function() {
            this.attributes['date'] = new Date(this.get('date'))
        }
    })
    var Dailies = PilesIO.Dailies = Backbone.Collection.extend({
        model:Daily,
        comparator:function(daily) {
            return daily.get('date')
        },
    })
	
    var Usage = PilesIO.Usage = Backbone.Model.extend({
        defaults:{
            "storage_total": 0,
            "usage_total_get": 0,
            "usage_total_put": 0,
        
            "storage_cost": 0.16,
            "usage_cost_get": 0.14,
            "usage_cost_put": 0.02
        },
        initialize:function() {
            this.url = 'http://' + PilesIO.App.APP_DOMAIN + '/piles/'+ (this.get('pid') || this.get('id')) + '/usage'
    		this.files = new FileCollection;
    		this.daily_puts = new Dailies;
    		this.daily_gets = new Dailies;
    		this.daily_sto = new Dailies;
        },
    });
	
	var Pile = PilesIO.Pile = Backbone.Model.extend({
		defaults:{
			welcome:false,
			cost_get:0.140,
			cost_put:0.020,
			cost_sto:0.160
		},
		initialize: function() {
		    var self = this;
    		this.urlRoot = 'http://'+PilesIO.App.APP_DOMAIN+'/piles',
			this.files = new FileCollection
			this.files.url = 'http://'+PilesIO.App.APP_DOMAIN+'/piles/'+this.id+'/files'
			this.usage = new Usage({'pid':this.get('id')})
			this.usage.fetch()
			
			this.bind('change',function(model) {
				var new_name = model.hasChanged('name')
				model.save({},{
					success: function() {
						if (new_name) self.trigger('renamesuccess')
					},
					error: function(data) {
						if (new_name) self.trigger('renamefailure','Rename error: Not a valid name!')
					}
				});
			});
			this.files.bind('add',function(model,collection) {
			    model.bind('uploadsuccess',function() {
			        self.fetch() // This is to refresh usage statistics
			    })
			})
		},
		validate: function(attrs) {
			if (attrs.name == '') {
				return "Name can't be blank";
			}
		},
	});



	/*************
	 * Views 
	 **************/
	var FileView = PilesIO.FileView = Backbone.View.extend({
		
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
			this.$el = $el;
			
			// Bind the view elem for draggability
			
			$el.draggable({
			    distance:15,
				containment: '.file-collection', 
				opacity: .75,
				helper:'clone',
				zIndex:600,
				appendTo: '.file-collection',
				start: function() { $(this).toggle() },
				stop: function() { $(this).toggle() }
			});
		
			if (this.model.get('pub')) $el.addClass('pub')
			
			/* Hover animations */
			/*$el.hover(
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
			)*/
			
			this.model.bind('destroy', this.doremove, this)
			this.model.bind('uploadprogress', this.updateprogress, this)
			this.model.bind('uploadsuccess', this.uploadsuccess, this)
			this.model.bind('uploaderror', this.uploaderror, this)
			this.model.bind('startworking', this.startworking, this)
			this.model.bind('stopworking', this.stopworking, this)
			this.model.bind('savesuccess', this.savesuccess, this)
			this.model.bind('saveerror', this.saveerror, this)
		},
		
		domodal:function() {
		    var self = this,
		        newmodal = new ModalFileView({model:this.model});
		    // Display modal using blockUI thingy
			$.blockUI({
				message: newmodal.render().el,
				css: {cursor:'auto'}
			})
			newmodal.postrender();
        
		},
		
		startworking:function() {
			$(this.el).addClass('working').draggable('option','disabled',true)
		},
		
		stopworking:function() {
			$(this.el).removeClass('working').draggable('option','disabled',false)
		},
		
		savesuccess:function(model) {
			var $el = $(this.el);
			model.get('pub') ? $el.addClass('pub') : $el.removeClass('pub');
			$el.effect("shake", { times:2, direction:'up', distance:10}, 100);
		},
		
		saveerror:function(prevattrs) {
			$el = $(this.el)
			left = $el.position().left;
			top = $el.position().top
			notify('error','There was an error saving your changes!')
			$(this.el).effect("shake", { times:2, direction:'left', distance:5}, 100)
				.fadeOut()
				.animate({left:prevattrs.x+'%',top:prevattrs.y+'%'}, 80)
				.fadeIn()
		},
		
		updateprogress: function(percent) {
			//console.log('Upload progress: '+ percent)
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
		
		uploaderror: function(errdata) {
		    notify('error','Failed to upload file!')
		},
		
		download: function() {
			//console.log('Download!')
			window.open(this.model.download_url())
		},
		
		doremove: function() {
		    var self = this;
		    this.$el.hide("shrink",function() {
			    self.remove()
			})
		},
		
		dodelete: function() {
			this.model.delete();
		},
		
		render: function() {
			c = _.template($('#file-tpl').html())
			var $el = $(this.el)
			$el.css('position','absolute')
			$el.css('left',this.model.get('x')+'%')
			$el.css('top',this.model.get('y')+'%')
			tpl_vals = this.model.toJSON()
			tpl_vals.ext || (tpl_vals.ext = '')
			$el.html(c(tpl_vals))
			
			return this;
		}
	});
	
	
	var SmallUsageView = PilesIO.SmallUsageView = Backbone.View.extend({
        initialize:function() {
            var self = this;
            this.$el = $(this.el);
    		this.model.bind('change',function() {
    		    self.render()
    		})
        },
        render:function() {
	        this.$el.html(_.template($('#small-usage-tpl').html(),this.model.toJSON()));
	        return this;
        }
	});
	
	
	var TwipsyView = PilesIO.TwipsyView = Backbone.View.extend({
	    initialize:function() {
	        var $el = $(this.el)
	        this.$el = $el
	    },
	    className:'twipsy below',
	    render:function() {
	        this.$el.html(_.template($('#twipsy-tpl').html(),this.model.toJSON()));
	        return this;
	    },
	    tip:function(tip,direction) {
	        this.$el.removeClass('below right left').addClass(direction)
	        this.$el.find('.twipsy-inner').html(tip)
	    }
	});


	var PileView = PilesIO.PileView = Backbone.View.extend({
			
		className:'pile-view',
		
		events:{
			'click .pile-view .rename': 'dorename',
		},
			
		initialize: function() {
			this.counter = 0;
			var $el = $(this.el),
				file_collection_selector = '.file-collection',
				self = this;
				$win = $(window)
			this.$el = $el;
				
			$el.height($win.height())
			$win.resize(function() {
				$el.height($win.height())
			})
			
			/* Handle EMPTY */
			if (this.model.files.models.length == 0) {
				$el.addClass('empty')
			} else {
				$el.removeClass('empty')
			}
			
			/* Setup bindings */
			this.model.files.bind('add', function(model,collection) {
				$el.removeClass('empty')
				self._render_file(model)
			});
			this.model.files.bind('remove', function() {
				if (self.model.files.models.length == 0) {
					$el.addClass('empty')	
				}
			});
			
			/* Setup searcher */
			this.$el.find('.searcher input').live('keyup', function(e) {
			    self.filefilter($(this).val())
			}).live('blur', function(e) {
			    if ($(this).val() == '') {
			        $(this).val('Search Files')
			    }
			}).live('focus', function(e) {
			    if ($(this).val() == 'Search Files') {
			        $(this).val('')
			    }
			})
			
            /* Setup tooltip thingy */
			this.twipsy = new TwipsyView({model:new Backbone.Model({tip:''})})
			this.twipsy.$el.hide()
			
			/* Handle renames */
			//this.model.bind('renamesuccess', this.renamedone, this);
			this.model.bind('renamefailure', function(err) { notify('error',err)}, this);
						

			// Setup fileuploader
			$el.fileupload({
				add:function(e, data) {
				    
				    if (data.files.length != 1) {
				        console.log('WARNING! Somehow got more than one file in add file');
			        }
				    
				    var fileobj = data.files[0],
				        filename = fileobj.name || fileobj.fileName,
					    namearray = filename.split('.'),
					 	ext = namearray.length>1 ? _.last(namearray) : '',
					 	
					 	// Figure out which elem this was dropped on
						$landed_elem = $(e.srcElement),
						
						// Calculate percent position of file elem
					    x = (e.offsetX-25)/$landed_elem.width()*100, // Subtract 15px so its more at center of mouse
					    y = (e.offsetY-25)/$landed_elem.height()*100,
					    
					    // Build the file model
					    filemodel = new File({
		    				x:x,
							y:y,
							name:filename,
							size:fileobj.size,
							type:fileobj.type,
							ext:ext,
							pub:$landed_elem.hasClass('public')
						});
    					
					file_upload_controller.setup_upload($el,filemodel,data)
                    
					self.model.files.add(filemodel)
					filemodel.save()
				},    
			    formData: file_upload_controller.get_form_data,
                multipart:true,
				paramName:'file',
				type:'POST',
				//forceIframeTransport:true,
			})
		},
		
		_do_percent_calculation: function($container,$elem,elem_offset) {
		    var container_offset = $container.offset(),
			    calc_left = (elem_offset.left-container_offset.left)/$container.width()*100,
			    calc_top = (elem_offset.top-container_offset.top)/$container.height()*100;
			return [calc_left,calc_top]
		},	
		_do_percent_positioning: function($container,$elem,elem_offset) {
            var calced = this._do_percent_calculation($container,$elem,elem_offset)
			$elem.appendTo($container)
		    $elem.css({left:calced[0]+'%', top:calced[1]+'%'})
			return calced
		},
		
		rebinddroppables:function() {
			
			var $el = this.$el,
				$priv = $el.find('.private'),
				$pub = $el.find('.public'),
				$trash = $el.find('.trash'),
				self = this;
				
			/* Trash droppable */
			$trash.droppable({
				drop:function(e,ui) {
					var elem = ui.draggable[0],
					    $elem = $(elem),
					    calced = self._do_percent_positioning($trash,$elem,ui.offset);
					// elem.view.model.set({x:calced[0], y:calced[1]}) <-- No need to save! We're deleting the file!
					ui.draggable[0].view.dodelete() // Thats kinda hacky...
				},
				tolerance:'intersect',
				hoverClass:'drophover',
				greedy:true,
			});
			

			/* Private well */
			$priv.droppable({
				drop:function(e,ui) {
					var elem = ui.draggable[0],
					    $elem = $(elem),
					    calced = self._do_percent_positioning($priv,$elem,ui.offset);
					elem.view.model.set({pub:false, x:calced[0], y:calced[1]})
				},
				tolerance:'intersect',
				hoverClass:'drophover',
				greedy:true,
			});
			
			/* Public Well */
			$pub.droppable({
				drop:function(e,ui) {
					var elem = ui.draggable[0],
					    $elem = $(elem),
					    calced = self._do_percent_positioning($pub,$elem,ui.offset);
					elem.view.model.set({pub:true, x:calced[0], y:calced[1]})
				},
				tolerance:'intersect',
				hoverClass:'drophover',
				greedy:true,
			});
		},
		
		filefilter: function(string) {
		    var self = this;
		        deemphasizer = function() {
    		        string = string.toLowerCase()
        		    self.$el.find('.file-view')
        	            .removeClass('deemphasized')
        	            .draggable( "option", "disabled", false )
        		    if (string && string != '') {
            		    self.$el.find('.file-name').not('[name*="'+string+'"]').closest('.file-view')
            		        .addClass('deemphasized')
            		        .draggable( "option", "disabled", true )
        		    }
        		    self.$el.dequeue('filefilter')
    		    };
		    //this.$el.queue('filefilter',deemphasizer)
		    //this.$el.dequeue('filefilter')
		    deemphasizer()
		},
		
		dorename: function() {
			var newname = prompt('New name for your Pile',this.model.get('name'))
			this.model.set({'name':newname})
		},
		renamedone: function() {
			window.location.href = '/' + this.model.get('name')
			//$(this.el).find('.pile-name span').html(this.model.get('name'))
		},
		
		
		
		_render_file: function(m) {
			if (m.get('pub')) {
				this.$pub.append((new FileView({model:m}).render().el));
			} else {
				this.$priv.append((new FileView({model:m}).render().el));
			}
			return this;
		},
		
		render: function() {
		    var self = this;
		    
		    console.log(this.model.toJSON())
		    
			this.$el.html($(_.template($('#pile-tpl').html(), this.model.toJSON())))

    	    this.$priv = this.$el.find('.private')
			this.$pub = this.$el.find('.public')

           	_.each(this.model.files.models,function(m) {
                self._render_file(m)
			})
			
			this.$el.find('.usage-container').html((new SmallUsageView({model:this.model.usage})).render().el)
			    .click(function() {location.href='http://'+PilesIO.App.APP_DOMAIN +'/'+ self.model.get('name') +'/usage' })
			
			this.$el.append(this.twipsy.render().el)
			//this.tooltip(this.$el.find('.usage-container'),'Click to view usage statistics.<br>(Statistics can be up to 30 mins delayed).','left')
			this.tooltip(this.$el.find('.searcher'), 'Click to search for files.')
			this.tooltip(this.$el.find('.trash'), 'Drag files here to delete them.','left')
			
			$('form').submit(function() {return false})
			
			this.rebinddroppables()
			return this;
		},
		
		tooltip: function($hover_elem,tip,direction) {
		    
	        if (!direction) direction='below';
		    
		    var self = this,
		        pos = {
		            below:'center top',
		            left:'right center ',
		            right:'left center '
		        }[direction],
		        off = {
		            below:'0 10',
		            left:'-25 0',
		            right:'25 0',
		        }[direction]
		    
		    $hover_elem.mousemove(function(ev){    
		        self.twipsy.tip(tip,direction);
                self.twipsy.$el.position({
                        my: pos,
                        of: ev,
                        offset: off,
                        collision: "fit"
                    });
            }).mouseout(function() {
                self.twipsy.$el.hide()
            }).mouseover(function() {
                self.twipsy.$el.show()
            })
		},
		
		/*add: function(file_model) {
			this.counter += 1;
			this.model.files.add(file_model)
			this.render();
		},*/
		
	});
	
	
	var ModalFileView = PilesIO.ModalFileView = Backbone.View.extend({
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
				attrs = this.model.toJSON(),
			    self = this;
			$el.html(tpl(attrs))
			return this
		},
		postrender:function() {
			// Setup circle player
			var self = this;
    	    this.myCirclePlayer = new CirclePlayer("#jquery_jplayer",
    	    {
                mp3: "http://" + PilesIO.App.APP_DOMAIN + "/piles/" + self.model.get('pid') + "/files/" + self.model.get('id') + "/content"
            },
        	{
        		cssSelectorAncestor: "#cp_container",
        		supplied: 'mp3, m4a, oga',
    			swfPath: PilesIO.App.CONTENT_DOMAIN + '/static/js/Jplayer.swf',
        	});
		},
		countdown:function() {
			var self = this
			setTimeout(function() {self.clear()},5000)
		},
		clear:function() {
			var self = this;
			this.myCirclePlayer.destroy()
			$.unblockUI()
			$(this.el).fadeOut(self.remove)
		}
	});


	var NotifyView = PilesIO.NotifyView = Backbone.View.extend({
		
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
	
	PilesIO.initialize = function() {
	    
	}
	
})(jQuery)
