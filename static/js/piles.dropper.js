(function() {
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  window.Piles = window.Piles || {};
  Piles.DropperView = Backbone.View.extend({
    el: "#dropper",
    initialize: function() {
      this.$doc = $(document);
      this.$box = this.$('.box');
      this.bounceAnim = _.throttle((__bind(function() {
        return this.$box.effect('bounce');
      }, this)), 1000);
      this.files = new Piles.FileCollection;
      return this.initDropper();
    },
    initDropper: function() {
      var self;
      self = this;
      this.$doc.on("dragover", _.bind(this.dragover, this));
      this.$doc.on("dragend", _.bind(this.dragend, this));
      return this.$doc.on("drop", _.bind(this.drop, this));
    },
    handleFile: function(fileobj) {
      var ext, filemodel, filename, namearray;
      filename = fileobj.name || fileobj.fileName;
      namearray = filename.split(".");
      ext = (namearray.length > 1 ? _.last(namearray) : "");
      filemodel = new Piles.File({
        name: filename,
        size: fileobj.size,
        type: fileobj.type,
        ext: ext,
        pub: false
      });
      this.files.add(filemodel);
      filemodel.save({}, {
        success: function() {
          return filemodel.associate_content(fileobj);
        }
      });
      return false;
    },
    drop: function(e) {
      var dataTransfer, file, _i, _len, _ref, _results;
      e.preventDefault();
      dataTransfer = e.dataTransfer || e.originalEvent.dataTransfer;
      if (!dataTransfer) {
        return;
      }
      _ref = dataTransfer.files;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        file = _ref[_i];
        _results.push(this.handleFile(file));
      }
      return _results;
    },
    dragover: function(e) {
      this.bounceAnim();
      return false;
    },
    dragend: function(e) {
      $('body').css('background-color', 'white');
      return false;
    }
  });
  Piles.dropperApp = function(options) {
    if (!options.pile) {
      throw "You must specify an `options.pile` object";
    }
    $(function() {
      return new Piles.DropperView;
    });
    return {
      model: new Pile(options.pile)
    };
  };
}).call(this);
