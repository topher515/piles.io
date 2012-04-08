window.ShinyBox or= {}
ShinyBox.Settings or= {}

tpl = (id)->
  $t = $('#'+id)
  if $t.length == 0
    throw "Template missing error: #" + id
  return _.template t.html()


ShinyBox.PublicFileRowView = Backbone.View.extend
  template = tpl('pubilc-file-row-tpl')


ShinyBox.FileTableView = Backbone.View.extend
  events:
    "click .delete":"trash"  
  template = tpl('file-row-tpl')
  initialize:->
    self = @
    @model.on 'fileupload:progress', (x)=>
      @$('.progress').addClass('active')
      @$('.bar').animate width: x+'%'
    @model.on 'fileupload:success', (x)=>
      @$('.bar').animate width: '100%', ()->
        self.$('.progress').removeClass('active')
    
  trash:->
    @model.trash()   
      
  render:->
    @setElement @template(@model.toJSON())
    @


ShinyBox.DropperApp = Backbone.View.extend
  className: "alert alert-info"
  template = tpl('dropper-app-tpl')
  initialize: ->
    self = @
    @$doc = $(document)
    @model.files.on 'add', (filemodel)=>
      self.$('#info').css(height:'auto', display:'block').slideDown ()->
      self.$('#info tbody').append (new ShinyBox.FileTableView model:filemodel).render().el
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

  render:()->
    @$el.html @template(@model.toJSON())
    return @


ShinyBox.ManagerApp = Backbone.View.extend
  
  initialize: ()->
    @publicFileView = new ShinyBox.FileTableView model:model
    @publicFileView = new ShinyBox.FileTableView model:model
    
  render:()->
    @$el


ShinyBox.Router = Backbone.Router.extend
  routes: 
    "dropper": "dropper"
    "manager": "manager"

ShinyBox.App = Backbone.View.extend
  initialize: (options)->
    @router = ShinyBox.Router()
    @router.on 'route:dropper' _.bind setDropperMode, @
    @router.on 'route:manager' _.bind setManagerMode, @
  
    @domain = options.domain
    @bucket = new XDFile.Bucket id:@domain
    @dropperApp = new ShinyBox.DropperApp model:@bucket
    @managerApp = new ShinyBox.ManagerApp model:@bucket
    
  setDropperMode: ()->
    @managerApp.remove()
    @dropperApp.$el.appendTo $('#content')
    
  setManagerMode: ()->
    @dropperApp.remove()
    @managerApp.$el.appendTo $('#content')


ShinyBox.bootstrap = (options)->
  
  _.defer ->
    # Setup so that ajax requests to the `APP_URL` are proxied through xdbackone
    jqAjax = $.ajax
    appUrl = ShinyBox.Settings.APP_URL
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
      },
      {
        remote: {
          ajax: {}
        }
      }
  
  $ ->
    window.shinyapp = ShinyBox.App domain:options.externDomain
    if options.externRpc
      dropperApp.on 'fileactivity:stop fileactivity:start', ()->
        w = Math.max dropperApp.$el.width(), dropperApp.$('table').width()
        options.externRpc.resize w, dropperApp.$el.height()

ShinyBox.xdmBootstrap = ()->
  externRpc = new easyXDM.Rpc {},
    {
      local:
        setDomain: (domain)->
          _.defer ()->
            ShinyBox.bootstrap externDomain:domain, externRpc:externRpc
      remote:
        resize: {}
          
    }
  