window.Piles = window.Piles or {}

Piles.DropperView = Backbone.View.extend
  el:"#dropper"
  initialize: ->
    @$doc = $(document)
    @$box = @$('.box')
    
    @bounceAnim = _.throttle (=>
        @$box.effect('bounce')
      ), 1000
    
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
    @bounceAnim()
    false
  
  dragend:(e)->
    $('body').css('background-color','white')
    false

Piles.dropperBootstrap = (options)->
  pid = window.location.hash.slice(1) 
  if not pid
    return window.location = 'http://localhost:8080/'
  
  window.dropperView = new Piles.DropperView model:(new Piles.Pile id:pid)