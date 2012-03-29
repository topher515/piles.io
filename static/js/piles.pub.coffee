(->
    Piles = window.Piles || {}
    
    (($) ->
      $.deserialize = (str, options) ->
        pairs = str.split(/&amp;|&/i)
        h = {}
        options = options or {}
        i = 0

        while i < pairs.length
          kv = pairs[i].split("=")
          kv[0] = decodeURIComponent(kv[0])
          if not options.except or options.except.indexOf(kv[0]) is -1
            if (/^\w+\[\w+\]$/).test(kv[0])
              matches = kv[0].match(/^(\w+)\[(\w+)\]$/)
              h[matches[1]] = {}  if typeof h[matches[1]] is "undefined"
              h[matches[1]][matches[2]] = decodeURIComponent(kv[1])
            else
              h[kv[0]] = decodeURIComponent(kv[1])
          i++
        h

      $.fn.deserialize = (options) ->
        $.deserialize $(this).serialize(), options
    ) jQuery
    
    
    Piles.PublicSessionView = Backbone.View.extend
        events:
            "dragover":"ignore"
            "gradend":"ignore"
            "drop":"dropped"
        ignore:->
            
        ###verifyMode:->
            # Init verifiers
            @verifier = Piles.Verifier url:@name+'/verify/'
            @verifier.bind 'verified', =>
                @fileMode()
        fileMode:->
            # Init file handlers
            @###

        dropped: (event)-> 
            e.preventDefault()
            return  unless e.dataTransfer

            _.each e.dataTransfer.files, (fileobj)=>
                $landedElem = $(e.srcElement)
                x = (e.offsetX - 25) / $landedElem.width() * 100
                y = (e.offsetY - 25) / $landedElem.height() * 100
                @model.newFile
                    meta:
                        x:x
                        y:y
                    fileobj:fileobj
            false

    Piles.Verifier = Backbone.Model.extend
        initialize:->
        url:->
            '/public-session/'

    Piles.VerifierView = Backbone.View.extend
        #template: _.template($('#verifier-tpl').html())
        initialize:->
            
        checkUrl:->
            if window.location.query?.code
                code = $.deserialize window.location.query.code

                    


    Piles.PubFileView = Backbone.View.extend
        template: _.template($('#pub-file-view-tpl').html())
        className:"pub-file-view"
        events:
            "cancel":"cancel"
        initialize:->
            @$el = $ el
            @model.bind 'upload:progress', @uploadProgress
        uploadProgress:->
            @$ '.progressbar'
        cancel:->
            @model.cancel()
        
    
    Piles.Verifier = Backbone.Model.extend
        defaults:
            verified:false
            code:''
        verify:->
            @fetch
                success:=>
                    @trigger 'verified', @
                error:=>
                    @set verified:false
                    @trigger 'verified', @

    Piles.PublicSession = Backbone.Model.extend
        initialize: (options)=>
            # Init files
            @uploadController = new Piles.FileUploadController
                uploadUrl: options.uploadUrl
            @files = new Backbone.Collection
            @initDragDrop()
        newFile: (filedata)=>
            meta = filedata.meta
            fileobj = filedata.fileobj
            namearray = filename.split(".")
            filemodel = new Piles.File
                x: meta.x
                y: meta.y
                name: meta.name or fileobj.name or fileobj.fileName
                size: fileobj.size
                type: fileobj.type
                ext: if meta.ext then meta.ext else (if namearray.length > 1 then _.last(namearray) else "").toLowerCase() 
                createdDate: new Date()
            filemodel.uploadController = @uploadController
            @files.add filemodel
            filemodel.save {},
                success: -> # Upon completion of persist, start uploading!
                    filemodel.associateContent fileobj


    Piles.bootstrapPublic = (options)->
        opts = _.extend
            uploadUrl: Piles.App.FILE_POST_URL
            
            , options
        new Piles.PublicSessionView 
            model:(new PublicSession opts)
            el:'#public-session'
)()