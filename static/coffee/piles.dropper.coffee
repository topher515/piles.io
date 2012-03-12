window.Piles or= {}

fileRowTpl = _.template '
<tr>
  <td><%= name %></td>
  <td><%= type %></td>
  <td><%= size %></td>
  <td><div class="progress progress-info progress-striped active"><div class="bar" style="width: 0%;"></div></div></td>
</tr>'

Piles.FileTableView = Backbone.View.extend
  initialize:->
    self = @
    @model.bind 'upload:progress', (x)=>
      @$('.progress').addClass('active')
      @$('.bar').animate width: x+'%'
    @model.bind 'upload:success', (x)=>
      @$('.bar').animate width: '100%', ()->
        self.$('.progress').removeClass('active')
        
      
  render:->
    @setElement (fileRowTpl @model.attributes)
    @

Piles.DropperApp = Backbone.View.extend
  el:'#content'
  initialize: ->
    self = @
    @$doc = $(document)
    @model.files.bind 'add', (filemodel)=>
      self.$('#info').css(height:'auto').slideDown()
      self.$('#info tbody').append (new Piles.FileTableView model:filemodel).render().el
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
    filemodel = new Piles.File
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

Piles.dropperBootstrap = (options)->
  pid = window.location.hash.slice(1) 
  if not pid
    return window.location = 'http://localhost:8080/'
  $ ->
    window.dropperApp = new Piles.DropperApp model:(new Piles.Pile id:pid)