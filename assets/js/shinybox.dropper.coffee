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

ShinyBox.bootstrap = (options)->
  $ ->
    window.dropperApp = new ShinyBox.DropperApp model:(new XDFile.Bucket id:options.domain)
    if options.rpc
      rpc = options.rpc
      dropperApp.on 'fileactivity:stop fileactivity:start', ()->
        w = Math.max dropperApp.$el.width(), dropperApp.$('table').width()
        rpc.resize w, dropperApp.$el.height()

ShinyBox.xdmBootstrap = ()->
  rpc = new easyXDM.Rpc {},
    {
      local:
        setDomain: (domain)->
          _.defer ()->
            ShinyBox.bootstrap domain:domain, rpc:rpc
      remote:
        resize: {}
          
    }
  