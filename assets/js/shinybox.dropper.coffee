window.ShinyBox or= {}

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
    @model.bind 'upload:progress', (x)=>
      @$('.progress').addClass('active')
      @$('.bar').animate width: x+'%'
    @model.bind 'upload:success', (x)=>
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
    @model.files.bind 'add', (filemodel)=>
      self.$('#info').css(height:'auto').slideDown()
      self.$('#info tbody').append (new ShinyBox.FileTableView model:filemodel).render().el
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
    filemodel = new ShinyBox.File
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

ShinyBox.dropperBootstrap = (options)->
  pid = window.location.hash.slice(1) 
  if not pid
    return window.location = 'http://localhost:8080/'
  $ ->
    window.dropperApp = new ShinyBox.DropperApp model:(new ShinyBox.Bucket id:)

ShinyBox.onMessage = (message,origin)->

ShinyBox.xdmBootstrap = ()->
  socket = new easyXDM.Socket
    onMessage: ShinyBox.onMessage
  
  