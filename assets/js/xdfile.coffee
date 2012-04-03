(->
if not window.Backbone 
  throw "XDFile requires the Backbone.js framework" 
if not window._
  throw "XDFile requires the Underscore.js utility library"
  
window.XDFile = window.XDFile || {}

XDFile.Settings or= {}

XDFile.IconGetter = ()->
  
  @base = "/static/img/"
  @default = @base + "file.png"
  
  @getIcon = (ext) ->
    img_icons =
      aac: "aac_icon.png"
      ai: "ai_icon.png"
      avi: "avi_icon.png"
      css: "css_icon.png"
      doc: "doc_icon.png"
      docx: "docx_icon.png"
      gif: "gif_icon.png"
      gzip: "gzip_icon.png"
      gz: "gzip_icon.png"
      html: "html_icon.png"
      jpeg: "jpeg_icon.png"
      jpg: "jpg_icon.png"
      js: "js_icon.png"
      ma: "ma_icon.png"
      mov: "mov_icon.png"
      mp: "mp_icon.png"
      mpeg2: "mpeg_icon.png"
      mp3: "mp3_icon.png"
      mp2: "mpeg_icon.png"
      mpg: "mpg_icon.png"
      mv: "mv_icon.png"
      pdf: "pdf_icon.png"
      php: "php_icon.png"
      php3: "php_icon.png"
      png: "png_icon.png"
      psd: "psd_icon.png"
      raw: "raw_icon.png"
      rtf: "rtf_icon.png"
      tar: "tar_icon.png"
      tiff: "tiff_icon.png"
      wav: "wav_icon.png"
      wmv: "wmv_icon.png"
      zip: "zip_icon.png"

    return @base + "/icons/" + img_icons[ext.toLowerCase()]  if img_icons[ext.toLowerCase()]
    return @default

    
XDFile.File = Backbone.Model.extend
  defaults:
    size: 0
    icon: "/static/img/file.png" # Remove this, this is display!
    ext: ""
    filetype: "Unknown File"
    thumb: ""
    progress: 0
    createdts: null
    successts: null
    key:""

  initialize: (options)->
    pos = {}
    if @get("x") > 100
      pos.x= 95
    else 
      pos.x= 0 if @get("x") < 0
    if @get("y") > 100
      pos.y= 90
    else 
      pos.y= 0 if @get("y") < 0
    if pos.x or pos.y
      @save pos

    @uploadController = new (options.uploadController or XDFile.FileUploadController)
    @unset 'uploadController', silent:true

  trash: ()->
    @set key:".trash"
    
    
    
  save: (attributes, options) ->
    options or (options = {})
    @trigger "filepersist:start"
  
    opts = 
      success:(m, r) =>
        @trigger "filepersist:success", m
        @trigger "filepersist:stop"
        options.success && options.success()
      error: (m, r) =>
        @trigger "filepersist:error"
        @trigger "filepersist:stop"
        options.error && options.error()
   
    Backbone.Model::save.call this, attributes, opts

  
  formData: ->
    key: @get("key")
    signature: @get("signature")
    policy: @get("policy")
    "Content-Type": @get("type")
    "Content-Disposition": (if @get("filetype").slice(0, 5) is "image" then "inline;" else "attachment;")

  startUpload:->
    @fileUploader.start()
    
  stopUpload:->
    @fileUploader.stop()

  associateContent: (file)->
    @fileUploader = new @uploadController.FileUploader 
      file:file
      formData: _.bind @formData, @
      url: XDFile.Settings.FILE_UPLOAD_URL or '/'
    # Proxy the fileUploader's events through this file
    @fileUploader.bind 'all', ()=>
      @trigger.apply this, arguments
      
    @startUpload()

    ###(new Thumbnailer).create(file).done((dataUrl, blob) ->
      self.save thumb: dataUrl
    ).fail ->###

  downloadUrl: ->
    "http://" + XDFile.Settings.APP_DOMAIN + "/xdfile/" + @get("pid") + "/files/" + @get("id") + "/content"

  delete: ->
    @trigger "filework:start"
    @destroy
      success:=> @trigger "filework:stop"
      error:=> notify "error", "Failed to delete file."

XDFile.FileCollection = Backbone.Collection.extend
  model: XDFile.File

XDFile.Bucket = Backbone.Model.extend
  initialize:()->
    self = @
    @files = new XDFile.FileCollection
    @files.url = ()=>
      self.url() + '/files/'
    fileActivity = 0
    actMinus = ->
      fileActivity -= 1
      if fileActivity == 0
        self.trigger 'fileactivity:stop'
    actPlus = ()->
      fileActivity += 1
      if fileActivity == 1
        self.trigger 'fileactivity:start'
        
    @files.on 'fileupload:start', actPlus
    @files.on 'fileupload:stop', actMinus
    @files.on 'filepersist:start', actPlus
    @files.on 'filepersist:stop', actMinus
    
  urlRoot:()->
    XDFile.Settings.APP_URL + 'buckets/'
  

XDFile.FileUploadController = (options)->
  ### Performs AJAX uploads
  
  ``options.formData`` specifies POST data
  ``options.file`` is the HTML5 FileObject representing the file data to upload
  ###
  options or= {}
  $el = $(options.el || '<div/>')
  postUrl = options.uploadUrl
  fuc = this
  defaultFormData = 
    AWSAccessKeyId: XDFile.Settings.AWS_ACCESS_KEY_ID
    acl: XDFile.Settings.STATIC_BUCKET_ACL

  @obj2tuple = (formobj)=>
    newfdata = []
    for key of formobj
      newfdata.push
        name: key
        value: formobj[key]
    newfdata

  @FileUploader = Backbone.Model.extend
    ### A File uploader for one file
    ###
    initialize: (options)->
      empty = ->

      throw new Error("No file to upload!")  unless options
      console.log "Uploading file: " + options.file.name

      @opts = _.extend({},
        multipart: true
        paramName: "file"
        type: "POST"
        # Setup event bindings for this jquery plugin to our system
        progress:(data)=>
          @trigger "fileupload:progress", parseInt(data.loaded / data.total * 100)
        fail:=>
          @trigger "fileupload:error"
          @trigger "fileupload:stop"
        done:=> 
          $el.fileupload "destroy"
          @trigger "fileupload:success"
          @trigger "fileupload:stop"
        
      , options)
    
      @opts.formData = ->
        f = (options?.formData() or {})
        fuc.obj2tuple (_.extend {}, defaultFormData, f)

      $el.fileupload @opts
    
    stop:->
      @jqXHR.abort()
    
    start:->
      @trigger "fileupload:start"
      @jqXHR = $el.fileupload "send", files: [ @opts.file ]
  @
)