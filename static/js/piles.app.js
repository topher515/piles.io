(function() {
  (function($) {
    var Dailies, Daily, File, FileCollection, FileUploadController, FileView, ModalFileView, NotifyView, Pile, PileView, SmallUsageView, TwipsyView, Usage, fuc, getUrl, get_icon, notify, onClient, rotate, stop_rotate, urlError;
    onClient = typeof exports === "undefined";
    if (window.Piles) {
      console.log("Piles already in global scope");
    } else {
      window.Piles = {};
    }
    jQuery.event.props.push("dataTransfer");
    get_icon = (new Piles.IconGetter()).getIcon;
    rotate = rotate = function(degree, plus, $elie) {
      var timer;
      $elie.css({
        WebkitTransform: "rotate(" + degree + "deg)"
      });
      $elie.css({
        "-moz-transform": "rotate(" + degree + "deg)"
      });
      if (!$elie || !$elie.get(0).stop_rotating) {
        timer = setTimeout(function() {
          return rotate(degree + plus, plus, $elie);
        }, 5);
        return console.log("still rotating...");
      }
    };
    stop_rotate = stop_rotate = function($elie) {
      $elie.get(0).stop_rotating = true;
      $elie.css({
        WebkitTransform: "rotate(0 deg)"
      });
      return $elie.css({
        "-moz-transform": "rotate(0 deg)"
      });
    };
    window.human_size = Piles.human_size = function(num) {
      var sizes, x, _results;
      sizes = ["bytes", "KB", "MB", "GB", "TB"];
      _results = [];
      for (x in sizes) {
        if (num < 1024.0) {
          return "" + num.toFixed(2) + " " + sizes[x];
        }
        _results.push(num = num / 1024.0);
      }
      return _results;
    };
    window.insert_spacers = Piles.insert_spacers = function(string, len) {
      var c, cursor, n, new_string, since_last_spacer;
      if (!len) {
        len = 10;
      }
      cursor = 0;
      new_string = [];
      since_last_spacer = 0;
      while (cursor < string.length) {
        c = string[cursor];
        if (c !== " " && c !== "\n" && c !== "\t" && c !== "-") {
          since_last_spacer++;
        } else {
          since_last_spacer = 0;
        }
        new_string.push(c);
        if (since_last_spacer > len) {
          new_string.push(" ");
          since_last_spacer = 0;
        }
        cursor++;
      }
      n = new_string.join("");
      return n;
    };
    getUrl = function(object) {
      if (!(object && object.url)) {
        return null;
      }
      if (_.isFunction(object.url)) {
        return object.url();
      } else {
        return object.url;
      }
    };
    urlError = function() {
      throw new Error("A \"url\" property or function must be specified");
    };
    window.notify = notify = function(level, msg) {
      return $("body").prepend((new NotifyView({
        model: {
          level: level,
          message: msg
        }
      })).render().el);
    };
    Piles.App = {
      AWS_BUCKET: "",
      FILE_POST_URL: "",
      AWS_ACCESS_KEY_ID: "",
      APP_DOMAIN: ""
    };
    Piles.jsonpSync = function(method, model, options) {
      var params, type;
      type = {
        create: "POST",
        update: "PUT",
        "delete": "DELETE",
        read: "GET"
      };
      [
        {
          method: method
        }
      ];
      params = _.extend({
        type: type,
        dataType: "jsonp"
      }, options);
      if (!params.url) {
        params.url = getUrl(model) || urlError();
      }
      if (type !== "DELETE") {
        params.data = {
          model: JSON.stringify(model.toJSON())
        };
      } else {
        params.data = {};
      }
      if (type === "PUT" || type === "DELETE" || type === "POST") {
        params.data._method = type;
        params.type = "GET";
        params.beforeSend = function(xhr) {
          return xhr.setRequestHeader("X-HTTP-Method-Override", type);
        };
      }
      return $.ajax(params);
    };
    FileUploadController = Piles.FileUploadController;
    fuc = new FileUploadController($("<div></div>"));
    File = Piles.File;
    FileCollection = Piles.FileCollection = Backbone.Collection.extend({
      model: File,
      comparator: function(file) {
        return -file.get("size");
      }
    });
    Daily = Piles.Daily = Backbone.Model.extend({
      initialize: function() {
        return this.attributes["date"] = new Date(this.get("date"));
      }
    });
    Dailies = Piles.Dailies = Backbone.Collection.extend({
      model: Daily,
      comparator: function(daily) {
        return daily.get("date");
      }
    });
    Usage = Piles.Usage = Backbone.Model.extend({
      defaults: {
        storage_cost: 0.16,
        storage_current_bytes: 0,
        storage_total_byte_hours: 0,
        storage_total_dollars: 0,
        storage_this_month_byte_hours: 0,
        storage_this_month_dollars: 0,
        usage_get_cost: 0.14,
        usage_get_total_bytes: 0,
        usage_get_total_dollars: 0,
        usage_get_this_month_bytes: 0,
        usage_get_this_month_dollars: 0,
        usage_put_cost: 0.02,
        usage_put_total_bytes: 0,
        usage_put_total_dollars: 0,
        usage_put_this_month_bytes: 0,
        usage_put_this_month_dollars: 0,
        freeloaders_this_month_max_dollars: 0.25,
        this_month_dollars: 0
      },
      initialize: function() {
        this.url = "http://" + Piles.App.APP_DOMAIN + "/piles/" + (this.get("pid") || this.get("id")) + "/usage";
        this.files = new FileCollection;
        this.daily_puts = new Dailies;
        this.daily_gets = new Dailies;
        return this.daily_sto = new Dailies;
      },
      dollars_this_month: function() {
        return this.get("storage_this_month_dollars") + this.get("usage_get_this_month_dollars") + this.get("usage_put_this_month_dollars");
      }
    });
    Pile = Piles.Pile = Backbone.Model.extend({
      defaults: {
        welcome: false,
        cost_get: 0.140,
        cost_put: 0.020,
        cost_sto: 0.160
      },
      initialize: function() {
        var self;
        self = this;
        this.urlRoot = "http://" + Piles.App.APP_DOMAIN + "/piles";
        this.files = new FileCollection;
        this.files.url = "http://" + Piles.App.APP_DOMAIN + "/piles/" + this.id + "/files";
        this.usage = new Usage({
          pid: this.get("id")
        });
        this.usage.fetch();
        this.bind("change", function(model) {
          var new_name;
          new_name = model.hasChanged("name");
          return model.save({}, {
            success: function() {
              if (new_name) {
                return self.trigger("renamesuccess");
              }
            },
            error: function(data) {
              if (new_name) {
                return self.trigger("renamefailure", "Rename error: Not a valid name!");
              }
            }
          });
        });
        return this.files.bind("add", function(model, collection) {
          return model.bind("uploadsuccess", function() {
            return self.usage.fetch();
          });
        });
      },
      validate: function(attrs) {
        if (attrs.name === "") {
          return "Name can't be blank";
        }
      }
    });
    FileView = Piles.FileView = Backbone.View.extend({
      events: {
        "dblclick .file-view .icon-display": "download",
        "click .file-view .delete": "dodelete",
        "click .file-view .info": "domodal"
      },
      className: "file-view",
      initialize: function() {
        var model, self;
        model = this.model;
        self = this;
        this.el.view = this;
        this.$el = $(this.el);
        this.$el.draggable({
          distance: 15,
          containment: ".file-collection",
          opacity: .75,
          helper: "clone",
          zIndex: 600,
          appendTo: ".file-collection",
          start: _.bind(this.startDrag, this),
          stop: _.bind(this.stopDrag, this),
          drag: _.bind(this.onDrag, this)
        });
        if (this.model.get("pub")) {
          this.$el.addClass("pub");
        }
        this.model.bind("destroy", this.doremove, this);
        this.model.bind("uploadprogress", this.updateprogress, this);
        this.model.bind("uploadsuccess", this.uploadsuccess, this);
        this.model.bind("uploaderror", this.uploaderror, this);
        this.model.bind("startworking", this.startworking, this);
        this.model.bind("stopworking", this.stopworking, this);
        this.model.bind("savesuccess", this.savesuccess, this);
        this.model.bind("saveerror", this.saveerror, this);
        return this.model.bind("change:thumb", this.set_thumb_src, this);
      },
      onDrag: function() {},
      startDrag: function() {
        return $(this).toggle();
      },
      stopDrag: function() {
        return $(this).toggle();
      },
      domodal: function() {
        var newmodal, self;
        self = this;
        newmodal = new ModalFileView({
          model: this.model
        });
        $.blockUI({
          message: newmodal.render().el,
          css: {
            cursor: "auto"
          }
        });
        return newmodal.postrender();
      },
      startworking: function() {
        return this.$el.addClass("working").draggable("option", "disabled", true);
      },
      stopworking: function() {
        return this.$el.removeClass("working").draggable("option", "disabled", false);
      },
      set_thumb_src: function(model) {
        return this.render();
      },
      savesuccess: function(model) {
        var $el;
        $el = $(this.el);
        if (model.get("pub")) {
          $el.addClass("pub");
        } else {
          $el.removeClass("pub");
        }
        return $el.effect("shake", {
          times: 2,
          direction: "up",
          distance: 7
        }, 100);
      },
      saveerror: function(prevattrs) {
        var $el, left, top;
        $el = $(this.el);
        left = $el.position().left;
        top = $el.position().top;
        notify("error", "There was an error saving your changes!");
        return $(this.el).effect("shake", {
          times: 2,
          direction: "left",
          distance: 5
        }, 100).fadeOut().animate({
          left: prevattrs.x + "%",
          top: prevattrs.y + "%"
        }, 80).fadeIn();
      },
      updateprogress: function(percent) {
        var $pbar;
        $pbar = $(this.el).find(".progressbar");
        if (percent <= 100) {
          $pbar.progressbar({
            value: percent
          });
          return $pbar.show();
        }
      },
      uploadsuccess: function() {
        var $pbar;
        $pbar = $(this.el).find(".progressbar").hide("slide", {
          direction: "right"
        });
        return this.stopworking();
      },
      uploaderror: function(errdata) {
        return notify("error", "Failed to upload file!");
      },
      download: function() {
        return window.open(this.model.download_url());
      },
      doremove: function() {
        var self;
        self = this;
        return this.$el.hide("shrink", function() {
          return self.remove();
        });
      },
      dodelete: function() {
        return this.model._delete();
      },
      render: function() {
        var $el, c, self, tpl_vals;
        c = _.template($("#file-tpl").html());
        $el = $(this.el);
        self = this;
        $el.css("position", "absolute");
        $el.css("left", this.model.get("x") + "%");
        $el.css("top", this.model.get("y") + "%");
        tpl_vals = this.model.toJSON();
        tpl_vals.ext || (tpl_vals.ext = "");
        $el.html(c(tpl_vals));
        $el.find("img.icon").error(function(e) {
          return $(this).attr("src", get_icon(self.model.get("ext")));
        });
        return this;
      }
    });
    SmallUsageView = Piles.SmallUsageView = Backbone.View.extend({
      initialize: function() {
        var self;
        self = this;
        this.$el = $(this.el);
        return this.model.bind("change", function() {
          return self.render();
        });
      },
      render: function() {
        this.$el.html(_.template($("#small-usage-tpl").html(), this.model.toJSON()));
        return this;
      }
    });
    TwipsyView = Piles.TwipsyView = Backbone.View.extend({
      initialize: function() {
        var $el;
        $el = $(this.el);
        return this.$el = $el;
      },
      className: "twipsy below",
      render: function() {
        this.$el.html(_.template($("#twipsy-tpl").html(), this.model.toJSON()));
        return this;
      },
      tip: function(tip, direction) {
        this.$el.removeClass("below right left").addClass(direction);
        return this.$el.find(".twipsy-inner").html(tip);
      }
    });
    PileView = Piles.PileView = Backbone.View.extend({
      className: "pile-view",
      events: {
        "click .pile-view .rename": "dorename"
      },
      initialize: function() {
        var $el, $win, file_collection_selector, self;
        this.counter = 0;
        $el = $(this.el);
        file_collection_selector = ".file-collection";
        self = this;
        $win = $(window);
        this.$el = $el;
        $el.height($win.height());
        $win.resize(function() {
          return $el.height($win.height());
        });
        if (this.model.files.models.length === 0) {
          $el.addClass("empty");
        } else {
          $el.removeClass("empty");
        }
        this.model.files.bind("add", function(model, collection) {
          $el.removeClass("empty");
          return self._render_file(model);
        });
        this.model.files.bind("remove", function() {
          if (self.model.files.models.length === 0) {
            return $el.addClass("empty");
          }
        });
        this._init_searcher();
        this.twipsy = new TwipsyView({
          model: new Backbone.Model({
            tip: ""
          })
        });
        this.twipsy.$el.hide();
        this.model.bind("renamefailure", (function(err) {
          return notify("error", err);
        }), this);
        return this._init_dropper();
      },
      _init_searcher: function() {
        var self;
        self = this;
        return this.$el.find(".searcher input").live("keyup", function(e) {
          return self.filefilter($(this).val());
        }).live("blur", function(e) {
          if ($(this).val() === "") {
            return $(this).val("Search Files");
          }
        }).live("focus", function(e) {
          if ($(this).val() === "Search Files") {
            return $(this).val("");
          }
        });
      },
      _init_dropper: function() {
        var self;
        self = this;
        $(document).bind("dragover dragend", function(e) {
          return false;
        });
        return $(document).bind("drop", function(e) {
          var $landed_elem, ext, filemodel, filename, fileobj, namearray, x, y;
          e.preventDefault();
          if (!e.dataTransfer) {
            return;
          }
          fileobj = e.dataTransfer.files[0];
          filename = fileobj.name || fileobj.fileName;
          namearray = filename.split(".");
          ext = (namearray.length > 1 ? _.last(namearray) : "");
          $landed_elem = $(e.srcElement);
          x = (e.offsetX - 25) / $landed_elem.width() * 100;
          y = (e.offsetY - 25) / $landed_elem.height() * 100;
          filemodel = new File({
            x: x,
            y: y,
            name: filename,
            size: fileobj.size,
            type: fileobj.type,
            ext: ext,
            pub: $landed_elem.hasClass("public")
          });
          self.model.files.add(filemodel);
          filemodel.save({}, {
            success: function() {
              return filemodel.associate_content(fileobj);
            }
          });
          return false;
        });
      },
      _do_percent_calculation: function($container, $elem, elem_offset) {
        var calc_left, calc_top, container_offset;
        container_offset = $container.offset();
        calc_left = (elem_offset.left - container_offset.left) / $container.width() * 100;
        calc_top = (elem_offset.top - container_offset.top) / $container.height() * 100;
        return [calc_left, calc_top];
      },
      _do_percent_positioning: function($container, $elem, elem_offset) {
        var calced;
        calced = this._do_percent_calculation($container, $elem, elem_offset);
        $elem.appendTo($container);
        $elem.css({
          left: calced[0] + "%",
          top: calced[1] + "%",
          position: "absolute"
        });
        return calced;
      },
      rebinddroppables: function() {
        var $el, $priv, $pub, $trash, self;
        $el = this.$el;
        $priv = $el.find(".private");
        $pub = $el.find(".public");
        $trash = $el.find(".trash");
        self = this;
        $trash.droppable({
          drop: function(e, ui) {
            var $elem, calced, elem;
            elem = ui.draggable[0];
            $elem = $(elem);
            calced = self._do_percent_positioning($trash, $elem, ui.offset);
            return ui.draggable[0].view.dodelete();
          },
          tolerance: "intersect",
          hoverClass: "drophover",
          greedy: true
        });
        $priv.droppable({
          drop: function(e, ui) {
            var $elem, calced, elem;
            elem = ui.draggable[0];
            $elem = $(elem);
            calced = self._do_percent_positioning($priv, $elem, ui.offset);
            return elem.view.model.save({
              pub: false,
              x: calced[0],
              y: calced[1]
            });
          },
          tolerance: "intersect",
          hoverClass: "drophover",
          greedy: true
        });
        return $pub.droppable({
          drop: function(e, ui) {
            var $elem, calced, elem;
            elem = ui.draggable[0];
            $elem = $(elem);
            calced = self._do_percent_positioning($pub, $elem, ui.offset);
            return elem.view.model.save({
              pub: true,
              x: calced[0],
              y: calced[1]
            });
          },
          tolerance: "intersect",
          hoverClass: "drophover",
          greedy: true
        });
      },
      filefilter: function(string) {
        var deemphasizer, self;
        self = this;
        deemphasizer = function() {
          string = string.toLowerCase();
          self.$el.find(".file-view").removeClass("deemphasized").draggable("option", "disabled", false);
          if (string && string !== "") {
            self.$el.find(".file-name").not("[name*=\"" + string + "\"]").closest(".file-view").addClass("deemphasized").draggable("option", "disabled", true);
          }
          return self.$el.dequeue("filefilter");
        };
        return deemphasizer();
      },
      dorename: function() {
        var newname;
        newname = prompt("New name for your Pile", this.model.get("name"));
        return this.model.save({
          name: newname
        });
      },
      renamedone: function() {
        return window.location.href = "/" + this.model.get("name");
      },
      _render_file: function(m) {
        if (m.get("pub")) {
          this.$pub.append(new FileView({
            model: m
          }).render().el);
        } else {
          this.$priv.append(new FileView({
            model: m
          }).render().el);
        }
        return this;
      },
      render: function() {
        var self;
        self = this;
        console.log(this.model.toJSON());
        this.$el.html($(_.template($("#pile-tpl").html(), this.model.toJSON())));
        this.$priv = this.$el.find(".private");
        this.$pub = this.$el.find(".public");
        _.each(this.model.files.models, function(m) {
          return self._render_file(m);
        });
        this.$el.find(".usage-container").html((new SmallUsageView({
          model: this.model.usage
        })).render().el).click(function() {
          return location.href = "http://" + Piles.App.APP_DOMAIN + "/" + self.model.get("name") + "/usage";
        });
        this.$el.append(this.twipsy.render().el);
        this.tooltip(this.$el.find(".searcher"), "Click to search for files.");
        this.tooltip(this.$el.find(".trash"), "Drag files here to delete them.", "left");
        $("form").submit(function() {
          return false;
        });
        this.rebinddroppables();
        return this;
      },
      tooltip: function($hover_elem, tip, direction) {
        var off_, pos, self;
        if (!direction) {
          direction = "below";
        }
        self = this;
        pos = {
          below: "center top",
          left: "right center ",
          right: "left center "
        };
        [
          {
            direction: direction
          }
        ];
        off_ = {
          below: "0 10",
          left: "-25 0",
          right: "25 0"
        };
        [
          {
            direction: direction
          }
        ];
        return $hover_elem.mousemove(function(ev) {
          self.twipsy.tip(tip, direction);
          return self.twipsy.$el.position({
            my: pos,
            of: ev,
            offset: off_,
            collision: "fit"
          });
        }).mouseout(function() {
          return self.twipsy.$el.hide();
        }).mouseover(function() {
          return self.twipsy.$el.show();
        });
      }
    });
    ModalFileView = Piles.ModalFileView = Backbone.View.extend({
      className: "modal modal-file-view",
      events: {
        "click .modal-file-view .close": "clear"
      },
      initialize: function() {
        var self;
        self = this;
        return $(".blockUI").click(self.clear);
      },
      render: function() {
        var $el, attrs, self, tpl;
        $el = $(this.el);
        tpl = _.template($("#modal-tpl").html());
        attrs = this.model.toJSON();
        self = this;
        $el.html(tpl(attrs));
        $el.find("img.icon").error(function(e) {
          return $(this).attr("src", get_icon(self.model.get("ext")));
        });
        return this;
      },
      postrender: function() {
        var self;
        self = this;
        if (self.model.get("type").slice(0, 5) !== "audio") {
          return;
        }
        return this.myCirclePlayer = new CirclePlayer("#jquery_jplayer", {
          mp3: "http://" + Piles.App.APP_DOMAIN + "/piles/" + self.model.get("pid") + "/files/" + self.model.get("id") + "/content"
        }, {
          preload: "none",
          cssSelectorAncestor: "#cp_container",
          supplied: "mp3, m4a, oga",
          swfPath: Piles.App.CONTENT_DOMAIN + "/static/js/Jplayer.swf"
        });
      },
      countdown: function() {
        var self;
        self = this;
        return setTimeout((function() {
          return self.clear();
        }), 5000);
      },
      clear: function() {
        var self;
        self = this;
        if (this.myCirclePlayer) {
          this.myCirclePlayer.destroy();
        }
        $.unblockUI();
        return $(this.el).fadeOut(self.remove);
      }
    });
    NotifyView = Piles.NotifyView = Backbone.View.extend({
      className: "alert-message",
      events: {
        "click .alert-message .close": "clear"
      },
      render: function() {
        var $el;
        $el = $(this.el).addClass(this.model.level);
        $el.html(_.template($("#notify-tpl").html(), this.model));
        this.countdown();
        return this;
      },
      countdown: function() {
        var self;
        self = this;
        return setTimeout((function() {
          return self.clear();
        }), 5000);
      },
      clear: function() {
        var self;
        self = this;
        return $(this.el).fadeOut(self.remove);
      }
    });
    return Piles.settings = function(options) {
      var socketboner;
      Piles.App = _.extend(Piles.App || {}, options);
      socketboner = new Socketbone.Client(options.SOCKETBONER_URL);
      return Backbone.sync = socketboner.sync;
    };
  })(jQuery);
}).call(this);
