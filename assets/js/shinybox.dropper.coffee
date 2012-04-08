window.ShinyBox or= {}
ShinyBox.Settings or= {}

tpl = (id)->
  $t = $('#'+id)
  if $t.length == 0
    throw "Template missing error: #{ id }"
  return _.template $t.html()


ShinyBox.FileTableRowView = Backbone.View.extend
  tagName: 'tr'
  events:
    "click .delete":"trash"  
  template: tpl 'file-row-tpl'
  initialize:->
    self = @
    @model.on 'fileupload:progress', (x)=>
      @$('.progress').addClass('active')
      @$('.bar').animate width: x+'%'
    @model.on 'fileupload:success', (x)=>
      @$('.bar').animate width: '100%', ()->
        self.$('.progress').removeClass 'active'
    
  trash:->
    @model.trash()   
      
  render:->
    @$el.html @template(@model.toJSON())
    @

ShinyBox.InboxFileTableRowView = ShinyBox.FileTableRowView.extend
  events:
    "click .delete":"trash"  
    "click .save":"keep"  
  template: tpl 'inbox-file-row-tpl'
  keep: ()->
    $saveBtn = @$el.find('.save').attr 'disabled', 'disabled'
    @model.save path:'', success:()->
      $saveBtn.removeAttr 'disabled'

ShinyBox.FileTableView = Backbone.View.extend
  className: 'table table-striped table-condensed'
  template: tpl 'file-table-tpl'
  TableRowView: ShinyBox.FileTableRowView
  initialize: ()->
    @_views = []
    @collection.on 'add', @_handleModelAdd, @
    @collection.on 'reset', @_handleReset, @
    @_handleReset @collection
    
  filter: (mdl)->
    mdl.get('path').slice(6) != 'inbox'

    
  _handleReset: (coll)->
    ishouldrender = @renderable
    @renderable = false
    @collection.each (_.bind @_handleModelAdd, @)
    @renderable = true
    if ishouldrender then @render()
    
  _handleModelAdd: (mdl)->
    if not @filter mdl
      return
    @_views.push (new @TableRowView(model:mdl))
    if @renderable then @render()
    
  render: ->
    @$el.html @template({})
    for view in @_views
      @$el.append view.render().el
    @
    
    
ShinyBox.InboxFileTableView = ShinyBox.FileTableView.extend
  TableRowView: ShinyBox.InboxFileTableRowView  
  filter: (mdl)->
    mdl.get('path').slice(6) == 'inbox'

ShinyBox.DropperApp = Backbone.View.extend
  className: "alert alert-info dropper-app"
  template: tpl 'dropper-app-tpl'
  events:
    "click .manage": "switchManagerMode"
  initialize: ->
    self = @
    @$doc = $(document)
    #@model.files.on 'add', (filemodel)=>
    #  self.$('#info').css(height:'auto', display:'block').slideDown ()->
    #  self.$('#info tbody').append (new ShinyBox.FileTableView model:filemodel).render().el
    @model.on 'all', =>
      self.trigger.apply self, arguments
    @initDropper()
    
  initDropper: ->
    self = this
    @$doc.on "dragover", _.bind @dragover, @
    @$doc.on "dragend", _.bind @dragend, @
    @$doc.on "drop", _.bind @drop, @

  handleFile:(fileobj)->
    filename = fileobj.name or fileobj.fileName
    namearray = filename.split(".")
    ext = (if namearray.length > 1 then _.last(namearray) else "")
    filemodel = new XDFile.File
      name: filename
      size: fileobj.size
      filetype: fileobj.type or 'unknown'
      ext: ext
      pub: false
    @model.files.add filemodel
    filemodel.save {},
      success: ->
        filemodel.associateContent fileobj
    false

  drop:(e)->
    e.preventDefault()
    dataTransfer = e.dataTransfer or e.originalEvent.dataTransfer
    return unless dataTransfer
    @handleFile file for file in dataTransfer.files
      
  dragover:(e)->
    false
  
  dragend:(e)->
    $('body').css('background-color','white')
    false

  switchManagerMode:->
    @trigger 'mode:manager'

  render:()->
    @$el.html @template(@model.toJSON())
    return @


ShinyBox.ManagerApp = Backbone.View.extend
  
  initialize: ()->
    @inboxFilesView = new ShinyBox.InboxFileTableView id:'inbox-file-table', collection:@model.files
    @savedFilesView = new ShinyBox.FileTableView id:'saved-file-table', collection:@model.files
    
  render:()->
    @$el.empty()
    @$el.append @inboxFilesView.render().el
    @$el.append @savedFilesView.render().el
    return @


#ShinyBox.Router = Backbone.Router.extend
#  routes: 
#    "dropper": "dropper"
#    "manager": "manager"

ShinyBox.App = Backbone.View.extend
  initialize: (options)->
    #@router = ShinyBox.Router()
    #@router.on 'route:dropper', @setDropperMode, @
    #@router.on 'route:manager', @setManagerMode, @
  
    @bucket = new XDFile.Bucket id:options.domain
    @dropperApp = new ShinyBox.DropperApp model:@bucket
    @managerApp = new ShinyBox.ManagerApp model:@bucket
    @dropperApp.on 'mode:manager', ()=>
      @setManagerMode()
    @managerApp.on 'mode:dropper', ()=>
      @setDropperMode()
    
  refresh: ()->
    @bucket.files.fetch()
    
  setDomain: (domain)->
    @bucket.set id:domain
    @refresh()
    
  setDropperMode: ()->
    @managerApp.remove()
    @dropperApp.render().$el.appendTo $('#content')
    @trigger 'minSize', 300, 100
    
  setManagerMode: ()->
    @dropperApp.remove()
    @managerApp.render().$el.appendTo $('#content')
    @trigger 'minSize', 700, 600

setupAjaxProxy = (options, complete)->
  # Setup so that ajax requests to the `APP_URL` are proxied through xdbackone
  jqAjax = $.ajax
  appUrl = options.appUrl
  xdbackbone = new easyXDM.Rpc {
      isHost: true
      remote: appUrl + 'xdbackbone.html'
      onReady: ()->
        $.ajax = ()->
          if typeof arguments[0] == 'string'
            url = arguments[0]
            obj = arguments[1]
          else if arguments[0].url
            url = arguments[0].url
            obj = arguments[0]
            
          if url and url.slice(0, appUrl.length) == appUrl
            # We call the xdbackbone ajax which takes callbacks appended to
            # then end of the arguments
            return xdbackbone.ajax.call @, url, obj, obj.success, obj.error
          else
            jqAjax.apply @, arguments
        complete && complete()
    },
    {
      remote: {
        ajax: {}
      }
    }
  




ShinyBox.xdmBootstrap = ()->

  deferred = $.Deferred()
  setupAjaxProxy (appUrl:"http://#{ ShinyBox.Settings.APP_DOMAIN }/"), deferred.resolve
  app = new ShinyBox.App({})
  app.setDropperMode()
  
  
  # Setup the crossdomain interface
  externRpc = new easyXDM.Rpc {},
    {
      local:
        setDomain: (domain)->
          deferred.then ->
            app.setDomain(domain)
          
              #dropperApp.on 'fileactivity:stop fileactivity:start', ()->
              #  w = Math.max dropperApp.$el.width(), dropperApp.$('table').width()
              #  options.externRpc.resize w, dropperApp.$el.height()
              
      remote:
        resize: {}
          
    }
  app.on 'minSize', externRpc.resize
  
  