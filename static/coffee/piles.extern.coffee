window.Piles or= {}

Extern = Piles.Extern = {}

Extern.resize = (width,height)->
	Piles.Extern.pileframe.style.width = parseInt(width) + 'px'
	Piles.Extern.pileframe.style.height = parseInt(height) + 'px'

Extern.buildIframe = (id,src,options)->
  el = document.createElement "iframe"
  el.setAttribute "id", id
  el.setAttribute "src", src
  el.style.border = '1px solid #DDD'
  el.style.width = options?.width or '640px'
  el.style.height = options?.height or '360px'
  el
    
Extern.bootstrap = (options)->
  ifr = Extern.buildIframe 'pileframe', 'http://localhost:9090/dropper'
  Extern.pileframe = ifr
  document.body.appendChild ifr
    
Extern.bootstrap()
  