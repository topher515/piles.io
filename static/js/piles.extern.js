(function() {
  var bootstrap, buildIframe;
  buildIframe = function(id, src, options) {
    var el;
    el = document.createElement("iframe");
    el.setAttribute("id", id);
    el.setAttribute("src", src);
    el.style.border = '1px solid #DDD';
    el.style.width = (options != null ? options.width : void 0) || '400px';
    el.style.height = (options != null ? options.height : void 0) || '300px';
    return el;
  };
  bootstrap = function(options) {
    var ifr;
    ifr = buildIframe(options.id, options.src);
    return document.body.appendChild(ifr);
  };
  bootstrap({
    id: 'pileframe',
    src: 'http://localhost:9090/dropper'
  });
}).call(this);
