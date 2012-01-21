(->
if not window.Backbone 
  throw "Piles requires the Backbone.js framework" 
if not window._
  throw "Piles requires the Underscore.js utility library"
  
window.Piles = window.Piles || {}
 
Piles.IconGetter = ()->
  
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
 
Piles.Pile = Backbone.Model.extend()
    
Piles.File = Backbone.Model.extend
  defaults:
    size: 0
    pid: null
    icon: "/static/img/file.png" # Remove this, this is display!
    ext: ""
    x: 0
    y: 0
    pub: false
    type: "Unknown File"
    thumb: ""
    progress: 0
    uploaded: false
    uploadedDate: null
    createdDate: null

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

    @uploadController = options.uploadController
    @unset 'uploadController', silent:true


  save: (attributes, options) ->
    options or (options = {})
    @trigger "persist:start"
    @trigger "work:start"
  
    stopwork = ()=> @trigger "work:stop"
    opts = {}
    opts.success = (m, r) ->
      stopwork()
      @trigger "persist:success", m
      options?.success()

    opts.error = (m, r) ->
      stopwork()
      @trigger "persist:error"
      options?.error()
   
    Backbone.Model::save.call this, attributes, (_.extend {},options,opts)

  
  formData: ->
    key: self.get("path")
    signature: self.get("signature")
    policy: self.get("policy")
    "Content-Type": self.get("type")
    "Content-Disposition": (if self.get("type").slice(0, 5) is "image" then "inline;" else "attachment;")

  startUpload:->
    @fileUploader.start()
    
  stopUpload:->
    @fileUploader.stop()

  associateContent: (file)->
    @fileUploader = new @uploadController.FileUploader 
      file:file
      formdata: @formData()
    # Proxy the fileUploader's events through this file
    @fileUploader.bind 'all', ()=>
      @trigger.apply this, arguments
      
    @startUpload()

    ###(new Thumbnailer).create(file).done((dataUrl, blob) ->
      self.save thumb: dataUrl
    ).fail ->###

  downloadUrl: ->
    "http://" + Piles.Settings.APP_DOMAIN + "/piles/" + @get("pid") + "/files/" + @get("id") + "/content"

  delete: ->
    @trigger "work:start"
    @destroy
      success:=> @trigger "work:stop"
      error:=> notify "error", "Failed to delete file."

Piles.FileCollection = Backbone.Collection.extend
  model: Piles.File

Piles.FileUploadController = (options)->
  ### Performs AJAX uploads
  
  ``options.formdata`` specifies POST data
  ``options.file`` is the HTML5 FileObject representing the file data to upload
  ###
  
  $el = $(options.el || '<div/>')
  postUrl = options.uploadUrl
  self = this
  defaultFormData = 
    AWSAccessKeyId: Piles.App.AWS_ACCESS_KEY_ID
    acl: Piles.App.APP_BUCKET_ACL

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

      options.formdata = @obj2tuple (_.extend defaultFormData options.formdata)

      opts = _.extend({},
        multipart: true
        paramName: "file"
        formata: {}
        type: "POST"
        url: uploadUrl

        # Setup event bindings for this jquery plugin to our system
        progress:=>
          @trigger "upload:progress", parseInt(data.loaded / data.total * 100)
        fail:=>
          @trigger "upload:error"
          @trigger "work:stop"
        done:=> 
          $el.fileupload "destroy"
          @trigger "upload:success"
          @trigger "work:stop"
        
      , options)

      $el.fileupload opts
    
    stop:->
      @jqXHR.abort()
    
    start:->
      @jqXHR = $el.fileupload "send", files: [ opts.file ]

)