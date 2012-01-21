window.Piles = window.Piles or {}

Piles.DropperView = Backbone.View.extend
  el:"#dropper"
  initialize: ->
    @$doc = $(document)
    @$box = @$('.box')
    
    @bounceAnim = _.throttle (=>
        @$box.effect('bounce')
      ), 1000
    
    @files = new Piles.FileCollection
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
    @files.add filemodel
    filemodel.save {},
      success: ->
        filemodel.associate_content fileobj
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

Piles.dropperApp = (options)->
  if not options.pile
    throw "You must specify an `options.pile` object"
  $ ->
    new Piles.DropperView
	  model:(new Piles.Pile(options.pile))