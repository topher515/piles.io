(function() {
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  (function() {
    var Piles;
    Piles = window.Piles || {};
    (function($) {
      $.deserialize = function(str, options) {
        var h, i, kv, matches, pairs;
        pairs = str.split(/&amp;|&/i);
        h = {};
        options = options || {};
        i = 0;
        while (i < pairs.length) {
          kv = pairs[i].split("=");
          kv[0] = decodeURIComponent(kv[0]);
          if (!options.except || options.except.indexOf(kv[0]) === -1) {
            if (/^\w+\[\w+\]$/.test(kv[0])) {
              matches = kv[0].match(/^(\w+)\[(\w+)\]$/);
              if (typeof h[matches[1]] === "undefined") {
                h[matches[1]] = {};
              }
              h[matches[1]][matches[2]] = decodeURIComponent(kv[1]);
            } else {
              h[kv[0]] = decodeURIComponent(kv[1]);
            }
          }
          i++;
        }
        return h;
      };
      return $.fn.deserialize = function(options) {
        return $.deserialize($(this).serialize(), options);
      };
    })(jQuery);
    Piles.PublicSessionView = Backbone.View.extend({
      events: {
        "dragover": "ignore",
        "gradend": "ignore",
        "drop": "dropped"
      },
      ignore: function() {},
      /*verifyMode:->
          # Init verifiers
          @verifier = Piles.Verifier url:@name+'/verify/'
          @verifier.bind 'verified', =>
              @fileMode()
      fileMode:->
          # Init file handlers
          @*/
      dropped: function(event) {
        e.preventDefault();
        if (!e.dataTransfer) {
          return;
        }
        _.each(e.dataTransfer.files, __bind(function(fileobj) {
          var $landedElem, x, y;
          $landedElem = $(e.srcElement);
          x = (e.offsetX - 25) / $landedElem.width() * 100;
          y = (e.offsetY - 25) / $landedElem.height() * 100;
          return this.model.newFile({
            meta: {
              x: x,
              y: y
            },
            fileobj: fileobj
          });
        }, this));
        return false;
      }
    });
    Piles.Verifier = Backbone.Model.extend({
      initialize: function() {},
      url: function() {
        return '/public-session/';
      }
    });
    Piles.VerifierView = Backbone.View.extend({
      initialize: function() {},
      checkUrl: function() {
        var code, _ref;
        if ((_ref = window.location.query) != null ? _ref.code : void 0) {
          return code = $.deserialize(window.location.query.code);
        }
      }
    });
    Piles.PubFileView = Backbone.View.extend({
      template: _.template($('#pub-file-view-tpl').html()),
      className: "pub-file-view",
      events: {
        "cancel": "cancel"
      },
      initialize: function() {
        this.$el = $(el);
        return this.model.bind('upload:progress', this.uploadProgress);
      },
      uploadProgress: function() {
        return this.$('.progressbar');
      },
      cancel: function() {
        return this.model.cancel();
      }
    });
    Piles.Verifier = Backbone.Model.extend({
      defaults: {
        verified: false,
        code: ''
      },
      verify: function() {
        return this.fetch({
          success: __bind(function() {
            return this.trigger('verified', this);
          }, this),
          error: __bind(function() {
            this.set({
              verified: false
            });
            return this.trigger('verified', this);
          }, this)
        });
      }
    });
    Piles.PublicSession = Backbone.Model.extend({
      initialize: __bind(function(options) {
        this.uploadController = new Piles.FileUploadController({
          uploadUrl: options.uploadUrl
        });
        this.files = new Backbone.Collection;
        return this.initDragDrop();
      }, this),
      newFile: __bind(function(filedata) {
        var filemodel, fileobj, meta, namearray;
        meta = filedata.meta;
        fileobj = filedata.fileobj;
        namearray = filename.split(".");
        filemodel = new Piles.File({
          x: meta.x,
          y: meta.y,
          name: meta.name || fileobj.name || fileobj.fileName,
          size: fileobj.size,
          type: fileobj.type,
          ext: meta.ext ? meta.ext : (namearray.length > 1 ? _.last(namearray) : "").toLowerCase(),
          createdDate: new Date()
        });
        filemodel.uploadController = this.uploadController;
        this.files.add(filemodel);
        return filemodel.save({}, {
          success: function() {
            return filemodel.associateContent(fileobj);
          }
        });
      }, this)
    });
    return Piles.bootstrapPublic = function(options) {
      var opts;
      opts = _.extend({
        uploadUrl: Piles.App.FILE_POST_URL
      }, options);
      return new Piles.PublicSessionView({
        model: new PublicSession(opts),
        el: '#public-session'
      });
    };
  })();
}).call(this);
