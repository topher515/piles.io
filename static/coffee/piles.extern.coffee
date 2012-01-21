buildIframe = (id,src,options)->
  el = document.createElement "iframe"
  el.setAttribute "id", id
  el.setAttribute "src", src
  el.style.border = '1px solid #DDD'
  el.style.width = options?.width or '400px'
  el.style.height = options?.height or '300px'
  el
    
bootstrap = (options)->
  ifr = buildIframe options.id, options.src
  document.body.appendChild ifr
    
bootstrap
  id:'pileframe'
  src:'http://localhost:9090/dropper'
  