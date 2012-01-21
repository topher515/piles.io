(($) ->
  onClient = typeof (exports) is "undefined"
  (if window.Piles then console.log("Piles already in global scope") else window.Piles = {})
  jQuery.event.props.push "dataTransfer"
  
  get_icon = (new Piles.IconGetter()).getIcon

  rotate = rotate = (degree, plus, $elie) ->
    $elie.css WebkitTransform: "rotate(" + degree + "deg)"
    $elie.css "-moz-transform": "rotate(" + degree + "deg)"
    if not $elie or not $elie.get(0).stop_rotating
      timer = setTimeout(->
        rotate degree + plus, plus, $elie
      , 5)
      console.log "still rotating..."

  stop_rotate = stop_rotate = ($elie) ->
    $elie.get(0).stop_rotating = true
    $elie.css WebkitTransform: "rotate(0 deg)"
    $elie.css "-moz-transform": "rotate(0 deg)"

  window.human_size = Piles.human_size = (num) ->
    sizes = [ "bytes", "KB", "MB", "GB", "TB" ]
    for x of sizes
      return "" + num.toFixed(2) + " " + sizes[x]  if num < 1024.0
      num = num / 1024.0

  window.insert_spacers = Piles.insert_spacers = (string, len) ->
    len = 10  unless len
    cursor = 0
    new_string = []
    since_last_spacer = 0
    while cursor < string.length
      c = string[cursor]
      if c isnt " " and c isnt "\n" and c isnt "\t" and c isnt "-"
        since_last_spacer++
      else
        since_last_spacer = 0
      new_string.push c
      if since_last_spacer > len
        new_string.push " "
        since_last_spacer = 0
      cursor++
    n = new_string.join("")
    n

  getUrl = (object) ->
    return null  unless object and object.url
    (if _.isFunction(object.url) then object.url() else object.url)

  urlError = ->
    throw new Error("A \"url\" property or function must be specified")

  window.notify = notify = (level, msg) ->
    $("body").prepend (new NotifyView(model:
      level: level
      message: msg
    )).render().el

  Piles.App =
    AWS_BUCKET: ""
    FILE_POST_URL: ""
    AWS_ACCESS_KEY_ID: ""
    APP_DOMAIN: ""

  Piles.jsonpSync = (method, model, options) ->
    type =
      create: "POST"
      update: "PUT"
      delete: "DELETE"
      read: "GET"
    [{method}]
    params = _.extend(
      type: type
      dataType: "jsonp"
    , options)
    params.url = getUrl(model) or urlError()  unless params.url
    unless type is "DELETE"
      params.data = model: JSON.stringify(model.toJSON())
    else
      params.data = {}
    if type is "PUT" or type is "DELETE" or type is "POST"
      params.data._method = type
      params.type = "GET"
      params.beforeSend = (xhr) ->
        xhr.setRequestHeader "X-HTTP-Method-Override", type
    $.ajax params

  FileUploadController = Piles.FileUploadController # Support old format
  fuc = new FileUploadController($("<div></div>"))

  File = Piles.File # Support old format

  FileCollection = Piles.FileCollection = Backbone.Collection.extend(
    model: File
    comparator: (file) ->
      -file.get("size")
  )
  Daily = Piles.Daily = Backbone.Model.extend(initialize: ->
    @attributes["date"] = new Date(@get("date"))
  )
  Dailies = Piles.Dailies = Backbone.Collection.extend(
    model: Daily
    comparator: (daily) ->
      daily.get "date"
  )
  Usage = Piles.Usage = Backbone.Model.extend(
    defaults:
      storage_cost: 0.16
      storage_current_bytes: 0
      storage_total_byte_hours: 0
      storage_total_dollars: 0
      storage_this_month_byte_hours: 0
      storage_this_month_dollars: 0
      usage_get_cost: 0.14
      usage_get_total_bytes: 0
      usage_get_total_dollars: 0
      usage_get_this_month_bytes: 0
      usage_get_this_month_dollars: 0
      usage_put_cost: 0.02
      usage_put_total_bytes: 0
      usage_put_total_dollars: 0
      usage_put_this_month_bytes: 0
      usage_put_this_month_dollars: 0
      freeloaders_this_month_max_dollars: 0.25
      this_month_dollars: 0

    initialize: ->
      @url = "http://" + Piles.App.APP_DOMAIN + "/piles/" + (@get("pid") or @get("id")) + "/usage"
      @files = new FileCollection
      @daily_puts = new Dailies
      @daily_gets = new Dailies
      @daily_sto = new Dailies

    dollars_this_month: ->
      @get("storage_this_month_dollars") + @get("usage_get_this_month_dollars") + @get("usage_put_this_month_dollars")
  )
  Pile = Piles.Pile = Backbone.Model.extend(
    defaults:
      welcome: false
      cost_get: 0.140
      cost_put: 0.020
      cost_sto: 0.160

    initialize: ->
      self = this
      @urlRoot = "http://" + Piles.App.APP_DOMAIN + "/piles"
      @files = new FileCollection

      @files.url = "http://" + Piles.App.APP_DOMAIN + "/piles/" + @id + "/files"
      @usage = new Usage(pid: @get("id"))
      @usage.fetch()
      @bind "change", (model) ->
        new_name = model.hasChanged("name")
        model.save {},
          success: ->
            self.trigger "renamesuccess"  if new_name

          error: (data) ->
            self.trigger "renamefailure", "Rename error: Not a valid name!"  if new_name

      @files.bind "add", (model, collection) ->
        model.bind "uploadsuccess", ->
          self.usage.fetch()

    validate: (attrs) ->
      "Name can't be blank"  if attrs.name is ""
  )
  FileView = Piles.FileView = Backbone.View.extend(
    events:
      "dblclick .file-view .icon-display": "download"
      "click .file-view .delete": "dodelete"
      "click .file-view .info": "domodal"

    className: "file-view"
    initialize: ->
      model = @model
      self = this
      @el.view = this
      @$el = $(@el)
      @$el.draggable
        distance: 15
        containment: ".file-collection"
        opacity: .75
        helper: "clone"
        zIndex: 600
        appendTo: ".file-collection"
        start: _.bind(@startDrag, this)
        stop: _.bind(@stopDrag, this)
        drag: _.bind(@onDrag, this)

      @$el.addClass "pub"  if @model.get("pub")
      @model.bind "destroy", @doremove, this
      @model.bind "uploadprogress", @updateprogress, this
      @model.bind "uploadsuccess", @uploadsuccess, this
      @model.bind "uploaderror", @uploaderror, this
      @model.bind "startworking", @startworking, this
      @model.bind "stopworking", @stopworking, this
      @model.bind "savesuccess", @savesuccess, this
      @model.bind "saveerror", @saveerror, this
      @model.bind "change:thumb", @set_thumb_src, this

    onDrag: ->

    startDrag: ->
      $(this).toggle()

    stopDrag: ->
      $(this).toggle()

    domodal: ->
      self = this
      newmodal = new ModalFileView(model: @model)
      $.blockUI
        message: newmodal.render().el
        css:
          cursor: "auto"

      newmodal.postrender()

    startworking: ->
      @$el.addClass("working").draggable "option", "disabled", true

    stopworking: ->
      @$el.removeClass("working").draggable "option", "disabled", false

    set_thumb_src: (model) ->
      @render()

    savesuccess: (model) ->
      $el = $(@el)
      (if model.get("pub") then $el.addClass("pub") else $el.removeClass("pub"))
      $el.effect "shake",
        times: 2
        direction: "up"
        distance: 7
      , 100

    saveerror: (prevattrs) ->
      $el = $(@el)
      left = $el.position().left
      top = $el.position().top
      notify "error", "There was an error saving your changes!"
      $(@el).effect("shake",
        times: 2
        direction: "left"
        distance: 5
      , 100).fadeOut().animate(
        left: prevattrs.x + "%"
        top: prevattrs.y + "%"
      , 80).fadeIn()

    updateprogress: (percent) ->
      $pbar = $(@el).find(".progressbar")
      if percent <= 100
        $pbar.progressbar value: percent
        $pbar.show()

    uploadsuccess: ->
      $pbar = $(@el).find(".progressbar").hide("slide",
        direction: "right"
      )
      @stopworking()

    uploaderror: (errdata) ->
      notify "error", "Failed to upload file!"

    download: ->
      window.open @model.download_url()

    doremove: ->
      self = this
      @$el.hide "shrink", ->
        self.remove()

    dodelete: ->
      @model._delete()

    render: ->
      c = _.template($("#file-tpl").html())
      $el = $(@el)
      self = this
      $el.css "position", "absolute"
      $el.css "left", @model.get("x") + "%"
      $el.css "top", @model.get("y") + "%"
      tpl_vals = @model.toJSON()
      tpl_vals.ext or (tpl_vals.ext = "")
      $el.html c(tpl_vals)
      $el.find("img.icon").error (e) ->
        $(this).attr "src", get_icon(self.model.get("ext"))

      this
  )
  SmallUsageView = Piles.SmallUsageView = Backbone.View.extend(
    initialize: ->
      self = this
      @$el = $(@el)
      @model.bind "change", ->
        self.render()

    render: ->
      @$el.html _.template($("#small-usage-tpl").html(), @model.toJSON())
      this
  )
  TwipsyView = Piles.TwipsyView = Backbone.View.extend(
    initialize: ->
      $el = $(@el)
      @$el = $el

    className: "twipsy below"
    render: ->
      @$el.html _.template($("#twipsy-tpl").html(), @model.toJSON())
      this

    tip: (tip, direction) ->
      @$el.removeClass("below right left").addClass direction
      @$el.find(".twipsy-inner").html tip
  )
  PileView = Piles.PileView = Backbone.View.extend(
    className: "pile-view"
    events:
      "click .pile-view .rename": "dorename"

    initialize: ->
      @counter = 0
      $el = $(@el)
      file_collection_selector = ".file-collection"
      self = this
      $win = $(window)
      @$el = $el
      $el.height $win.height()
      $win.resize ->
        $el.height $win.height()

      if @model.files.models.length is 0
        $el.addClass "empty"
      else
        $el.removeClass "empty"
      @model.files.bind "add", (model, collection) ->
        $el.removeClass "empty"
        self._render_file model

      @model.files.bind "remove", ->
        $el.addClass "empty"  if self.model.files.models.length is 0

      @_init_searcher()
      @twipsy = new TwipsyView(model: new Backbone.Model(tip: ""))
      @twipsy.$el.hide()
      @model.bind "renamefailure", ((err) ->
        notify "error", err
      ), this
      @_init_dropper()

    _init_searcher: ->
      self = this
      @$el.find(".searcher input").live("keyup", (e) ->
        self.filefilter $(this).val()
      ).live("blur", (e) ->
        $(this).val "Search Files"  if $(this).val() is ""
      ).live "focus", (e) ->
        $(this).val ""  if $(this).val() is "Search Files"

    _init_dropper: ->
      self = this
      $(document).bind "dragover dragend", (e) ->
        false

      $(document).bind "drop", (e) ->
        e.preventDefault()
        return  unless e.dataTransfer
        fileobj = e.dataTransfer.files[0]
        filename = fileobj.name or fileobj.fileName
        namearray = filename.split(".")
        ext = (if namearray.length > 1 then _.last(namearray) else "")
        $landed_elem = $(e.srcElement)
        x = (e.offsetX - 25) / $landed_elem.width() * 100
        y = (e.offsetY - 25) / $landed_elem.height() * 100
        filemodel = new File(
          x: x
          y: y
          name: filename
          size: fileobj.size
          type: fileobj.type
          ext: ext
          pub: $landed_elem.hasClass("public")
        )
        self.model.files.add filemodel
        filemodel.save {},
          success: ->
            filemodel.associate_content fileobj

        false

    _do_percent_calculation: ($container, $elem, elem_offset) ->
      container_offset = $container.offset()
      calc_left = (elem_offset.left - container_offset.left) / $container.width() * 100
      calc_top = (elem_offset.top - container_offset.top) / $container.height() * 100
      [ calc_left, calc_top ]

    _do_percent_positioning: ($container, $elem, elem_offset) ->
      calced = @_do_percent_calculation($container, $elem, elem_offset)
      $elem.appendTo $container
      $elem.css
        left: calced[0] + "%"
        top: calced[1] + "%"
        position: "absolute"

      calced

    rebinddroppables: ->
      $el = @$el
      $priv = $el.find(".private")
      $pub = $el.find(".public")
      $trash = $el.find(".trash")
      self = this
      $trash.droppable
        drop: (e, ui) ->
          elem = ui.draggable[0]
          $elem = $(elem)
          calced = self._do_percent_positioning($trash, $elem, ui.offset)
          ui.draggable[0].view.dodelete()

        tolerance: "intersect"
        hoverClass: "drophover"
        greedy: true

      $priv.droppable
        drop: (e, ui) ->
          elem = ui.draggable[0]
          $elem = $(elem)
          calced = self._do_percent_positioning($priv, $elem, ui.offset)
          elem.view.model.save
            pub: false
            x: calced[0]
            y: calced[1]

        tolerance: "intersect"
        hoverClass: "drophover"
        greedy: true

      $pub.droppable
        drop: (e, ui) ->
          elem = ui.draggable[0]
          $elem = $(elem)
          calced = self._do_percent_positioning($pub, $elem, ui.offset)
          elem.view.model.save
            pub: true
            x: calced[0]
            y: calced[1]

        tolerance: "intersect"
        hoverClass: "drophover"
        greedy: true

    filefilter: (string) ->
      self = this
      deemphasizer = ->
        string = string.toLowerCase()
        self.$el.find(".file-view").removeClass("deemphasized").draggable "option", "disabled", false
        self.$el.find(".file-name").not("[name*=\"" + string + "\"]").closest(".file-view").addClass("deemphasized").draggable "option", "disabled", true  if string and string isnt ""
        self.$el.dequeue "filefilter"

      deemphasizer()

    dorename: ->
      newname = prompt("New name for your Pile", @model.get("name"))
      @model.save name: newname

    renamedone: ->
      window.location.href = "/" + @model.get("name")

    _render_file: (m) ->
      if m.get("pub")
        @$pub.append (new FileView(model: m).render().el)
      else
        @$priv.append (new FileView(model: m).render().el)
      this

    render: ->
      self = this
      console.log @model.toJSON()
      @$el.html $(_.template($("#pile-tpl").html(), @model.toJSON()))
      @$priv = @$el.find(".private")
      @$pub = @$el.find(".public")
      _.each @model.files.models, (m) ->
        self._render_file m

      @$el.find(".usage-container").html((new SmallUsageView(model: @model.usage)).render().el).click ->
        location.href = "http://" + Piles.App.APP_DOMAIN + "/" + self.model.get("name") + "/usage"

      @$el.append @twipsy.render().el
      @tooltip @$el.find(".searcher"), "Click to search for files."
      @tooltip @$el.find(".trash"), "Drag files here to delete them.", "left"
      $("form").submit ->
        false

      @rebinddroppables()
      this

    tooltip: ($hover_elem, tip, direction) ->
      direction = "below"  unless direction
      self = this
      pos =
        below: "center top"
        left: "right center "
        right: "left center "
      [{direction}]
      off_ =
        below: "0 10"
        left: "-25 0"
        right: "25 0"
      [{direction}]
      $hover_elem.mousemove((ev) ->
        self.twipsy.tip tip, direction
        self.twipsy.$el.position
          my: pos
          of: ev
          offset: off_
          collision: "fit"
      ).mouseout(->
        self.twipsy.$el.hide()
      ).mouseover ->
        self.twipsy.$el.show()
  )
  ModalFileView = Piles.ModalFileView = Backbone.View.extend(
    className: "modal modal-file-view"
    events:
      "click .modal-file-view .close": "clear"

    initialize: ->
      self = this
      $(".blockUI").click self.clear

    render: ->
      $el = $(@el)
      tpl = _.template($("#modal-tpl").html())
      attrs = @model.toJSON()
      self = this
      $el.html tpl(attrs)
      $el.find("img.icon").error (e) ->
        $(this).attr "src", get_icon(self.model.get("ext"))

      this

    postrender: ->
      self = this
      return  unless self.model.get("type").slice(0, 5) is "audio"
      @myCirclePlayer = new CirclePlayer("#jquery_jplayer",
        mp3: "http://" + Piles.App.APP_DOMAIN + "/piles/" + self.model.get("pid") + "/files/" + self.model.get("id") + "/content"
      ,
        preload: "none"
        cssSelectorAncestor: "#cp_container"
        supplied: "mp3, m4a, oga"
        swfPath: Piles.App.CONTENT_DOMAIN + "/static/js/Jplayer.swf"
      )

    countdown: ->
      self = this
      setTimeout (->
        self.clear()
      ), 5000

    clear: ->
      self = this
      @myCirclePlayer.destroy()  if @myCirclePlayer
      $.unblockUI()
      $(@el).fadeOut self.remove
  )
  NotifyView = Piles.NotifyView = Backbone.View.extend(
    className: "alert-message"
    events:
      "click .alert-message .close": "clear"

    render: ->
      $el = $(@el).addClass(@model.level)
      $el.html _.template($("#notify-tpl").html(), @model)
      @countdown()
      this

    countdown: ->
      self = this
      setTimeout (->
        self.clear()
      ), 5000

    clear: ->
      self = this
      $(@el).fadeOut self.remove
  )
  Piles.settings = (options) ->
    Piles.App = _.extend(Piles.App or {}, options)
    socketboner = new Socketbone.Client(options.SOCKETBONER_URL)
    Backbone.sync = socketboner.sync
) jQuery