(function() {
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  (function() {});
  if (!window.Backbone) {
    throw "Piles requires the Backbone.js framework";
  }
  if (!window._) {
    throw "Piles requires the Underscore.js utility library";
  }
  window.Piles = window.Piles || {};
  Piles.IconGetter = function() {
    this.base = "/static/img/";
    this["default"] = this.base + "file.png";
    return this.getIcon = function(ext) {
      var img_icons;
      img_icons = {
        aac: "aac_icon.png",
        ai: "ai_icon.png",
        avi: "avi_icon.png",
        css: "css_icon.png",
        doc: "doc_icon.png",
        docx: "docx_icon.png",
        gif: "gif_icon.png",
        gzip: "gzip_icon.png",
        gz: "gzip_icon.png",
        html: "html_icon.png",
        jpeg: "jpeg_icon.png",
        jpg: "jpg_icon.png",
        js: "js_icon.png",
        ma: "ma_icon.png",
        mov: "mov_icon.png",
        mp: "mp_icon.png",
        mpeg2: "mpeg_icon.png",
        mp3: "mp3_icon.png",
        mp2: "mpeg_icon.png",
        mpg: "mpg_icon.png",
        mv: "mv_icon.png",
        pdf: "pdf_icon.png",
        php: "php_icon.png",
        php3: "php_icon.png",
        png: "png_icon.png",
        psd: "psd_icon.png",
        raw: "raw_icon.png",
        rtf: "rtf_icon.png",
        tar: "tar_icon.png",
        tiff: "tiff_icon.png",
        wav: "wav_icon.png",
        wmv: "wmv_icon.png",
        zip: "zip_icon.png"
      };
      if (img_icons[ext.toLowerCase()]) {
        return this.base + "/icons/" + img_icons[ext.toLowerCase()];
      }
      return this["default"];
    };
  };
  Piles.Pile = Backbone.Model.extend();
  Piles.File = Backbone.Model.extend({
    defaults: {
      size: 0,
      pid: null,
      icon: "/static/img/file.png",
      ext: "",
      x: 0,
      y: 0,
      pub: false,
      type: "Unknown File",
      thumb: "",
      progress: 0,
      uploaded: false,
      uploadedDate: null,
      createdDate: null
    },
    initialize: function(options) {
      var pos;
      pos = {};
      if (this.get("x") > 100) {
        pos.x = 95;
      } else {
        if (this.get("x") < 0) {
          pos.x = 0;
        }
      }
      if (this.get("y") > 100) {
        pos.y = 90;
      } else {
        if (this.get("y") < 0) {
          pos.y = 0;
        }
      }
      if (pos.x || pos.y) {
        this.save(pos);
      }
      this.uploadController = options.uploadController;
      return this.unset('uploadController', {
        silent: true
      });
    },
    save: function(attributes, options) {
      var opts, stopwork;
      options || (options = {});
      this.trigger("persist:start");
      this.trigger("work:start");
      stopwork = __bind(function() {
        return this.trigger("work:stop");
      }, this);
      opts = {};
      opts.success = function(m, r) {
        stopwork();
        this.trigger("persist:success", m);
        return options != null ? options.success() : void 0;
      };
      opts.error = function(m, r) {
        stopwork();
        this.trigger("persist:error");
        return options != null ? options.error() : void 0;
      };
      return Backbone.Model.prototype.save.call(this, attributes, _.extend({}, options, opts));
    },
    formData: function() {
      return {
        key: self.get("path"),
        signature: self.get("signature"),
        policy: self.get("policy"),
        "Content-Type": self.get("type"),
        "Content-Disposition": (self.get("type").slice(0, 5) === "image" ? "inline;" : "attachment;")
      };
    },
    startUpload: function() {
      return this.fileUploader.start();
    },
    stopUpload: function() {
      return this.fileUploader.stop();
    },
    associateContent: function(file) {
      this.fileUploader = new this.uploadController.FileUploader({
        file: file,
        formdata: this.formData()
      });
      this.fileUploader.bind('all', __bind(function() {
        return this.trigger.apply(this, arguments);
      }, this));
      return this.startUpload();
      /*(new Thumbnailer).create(file).done((dataUrl, blob) ->
        self.save thumb: dataUrl
      ).fail ->*/
    },
    downloadUrl: function() {
      return "http://" + Piles.Settings.APP_DOMAIN + "/piles/" + this.get("pid") + "/files/" + this.get("id") + "/content";
    },
    "delete": function() {
      this.trigger("work:start");
      return this.destroy({
        success: __bind(function() {
          return this.trigger("work:stop");
        }, this),
        error: __bind(function() {
          return notify("error", "Failed to delete file.");
        }, this)
      });
    }
  });
  Piles.FileCollection = Backbone.Collection.extend({
    model: Piles.File
  });
  Piles.FileUploadController = function(options) {
    /* Performs AJAX uploads
    
    ``options.formdata`` specifies POST data
    ``options.file`` is the HTML5 FileObject representing the file data to upload
    */
    var $el, defaultFormData, postUrl, self;
    $el = $(options.el || '<div/>');
    postUrl = options.uploadUrl;
    self = this;
    defaultFormData = {
      AWSAccessKeyId: Piles.App.AWS_ACCESS_KEY_ID,
      acl: Piles.App.APP_BUCKET_ACL
    };
    this.obj2tuple = __bind(function(formobj) {
      var key, newfdata;
      newfdata = [];
      for (key in formobj) {
        newfdata.push;
        ({
          name: key,
          value: formobj[key]
        });
      }
      return newfdata;
    }, this);
    return this.FileUploader = Backbone.Model.extend({
      /* A File uploader for one file
      */
      initialize: function(options) {
        var empty, opts;
        empty = function() {};
        if (!options) {
          throw new Error("No file to upload!");
        }
        console.log("Uploading file: " + options.file.name);
        options.formdata = this.obj2tuple(_.extend(defaultFormData(options.formdata)));
        opts = _.extend({}, {
          multipart: true,
          paramName: "file",
          formata: {},
          type: "POST",
          url: uploadUrl,
          progress: __bind(function() {
            return this.trigger("upload:progress", parseInt(data.loaded / data.total * 100));
          }, this),
          fail: __bind(function() {
            this.trigger("upload:error");
            return this.trigger("work:stop");
          }, this),
          done: __bind(function() {
            $el.fileupload("destroy");
            this.trigger("upload:success");
            return this.trigger("work:stop");
          }, this)
        }, options);
        return $el.fileupload(opts);
      },
      stop: function() {
        return this.jqXHR.abort();
      },
      start: function() {
        return this.jqXHR = $el.fileupload("send", {
          files: [opts.file]
        });
      }
    });
  };
}).call(this);
