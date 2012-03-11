(function() {
  var Extern;
  window.Piles || (window.Piles = {});
  Extern = Piles.Extern = {};
  Extern.resize = function(width, height) {
    Piles.Extern.pileframe.style.width = parseInt(width) + 'px';
    return Piles.Extern.pileframe.style.height = parseInt(height) + 'px';
  };
  Extern.buildIframe = function(id, src, options) {
    var el;
    el = document.createElement("iframe");
    el.setAttribute("id", id);
    el.setAttribute("src", src);
    el.style.border = '1px solid #DDD';
    el.style.width = (options != null ? options.width : void 0) || '640px';
    el.style.height = (options != null ? options.height : void 0) || '360px';
    return el;
  };
  Extern.bootstrap = function(options) {
    var ifr;
    ifr = Extern.buildIframe('pileframe', 'http://localhost:9090/dropper');
    Extern.pileframe = ifr;
    return document.body.appendChild(ifr);
  };
  Extern.bootstrap();
}).call(this);
