(function() {
  var fileRowTpl;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  window.Piles || (window.Piles = {});
  fileRowTpl = _.template("<tr>  <td><%= name %></td><td><%= type %></td><td><%= size %></td></tr>");
  Piles.FileTableView = Backbone.View.extend({
    render: function() {
      this.el = fileRowTpl(this.model.attributes);
      return this;
    }
  });
  Piles.DropperApp = Backbone.View.extend({
    el: "#content",
    initialize: function() {
      this.$el = $(this.el);
      this.$doc = $(document);
      this.model.files.bind('add', __bind(function(filemodel) {
        return this.$('tbody').append((new Piles.FileTableView({
          model: filemodel
        })).render());
      }, this));
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
      this.model.files.add(filemodel);
      filemodel.save({}, {
        success: function() {
          return filemodel.associateContent(fileobj);
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
      return false;
    },
    dragend: function(e) {
      $('body').css('background-color', 'white');
      return false;
    }
  });
  Piles.dropperBootstrap = function(options) {
    var pid;
    pid = window.location.hash.slice(1);
    if (!pid) {
      return window.location = 'http://localhost:8080/';
    }
    return window.dropperApp = new Piles.DropperApp({
      model: new Piles.Pile({
        id: pid
      })
    });
  };
}).call(this);
