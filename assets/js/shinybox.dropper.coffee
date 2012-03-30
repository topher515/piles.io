window.ShinyBox or= {}
ShinyBox.Settings or= {}

fileRowTpl = _.template '<tr>
  <td><%= name %></td>
  <td><%= type %></td>
  <td><%= size %></td>
  <td><div class="progress progress-info progress-striped active"><div class="bar" style="width: 0%;"></div></div></td>
  <td><button class="delete btn btn-danger btn-mini">Delete</button></td>
</tr>'

ShinyBox.FileTableView = Backbone.View.extend
  events:
    "click .delete":"trash"  

  initialize:->
    self = @
    @model.on 'upload:progress', (x)=>
      @$('.progress').addClass('active')
      @$('.bar').animate width: x+'%'
    @model.on 'upload:success', (x)=>
      @$('.bar').animate width: '100%', ()->
        self.$('.progress').removeClass('active')
    
  trash:->
    @model.trash()   
      
  render:->
    @setElement (fileRowTpl @model.attributes)
    @

ShinyBox.DropperApp = Backbone.View.extend
  el:'#content'
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
      type: fileobj.type
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


getValue = (object, prop) ->
  return null  unless object and object[prop]
  (if _.isFunction(object[prop]) then object[prop]() else object[prop])

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
            else if arguments[0].url
              url = arguments[0].url
            
            if url and url.slice(0, appUrl.length) == appUrl
              return xdbackbone.ajax.apply @, arguments
            else
              jqAjax.apply @, arguments
      },
      {
        remote: {
          ajax: {}
        }
      }
  
  $ ->
    window.dropperApp = new ShinyBox.DropperApp model:(new XDFile.Bucket id:options.externDomain)
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
  