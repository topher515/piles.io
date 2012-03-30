window.ShinyBox or= {}

Extern = ShinyBox.Extern = {}

Extern.resize = (width,height)->
  el = document.getElementById 'shinybox'
  ifr = el.getElementsByTagName('iframe')[0]
  ifr.style.width = parseInt(width) + 'px'
  ifr.style.height = parseInt(height) + 'px'

Extern.bootstrap = (options)->
  # Setup `consumer`--container document
  rpc = new easyXDM.Rpc {
    remote: options.remote
    container: options.container
    props: 
      style: 
        border: "1px solid #DDD"
        width: '300px'
        height: '80px'
    onReady: (->
      rpc.setDomain options.domain)
  }, {
      local:
        resize: Extern.resize
      remote:
        setDomain: {}
  }
  

opts = {}
for e in (window._shiny or [])
  opts[e[0]] = e[1]
Extern.bootstrap(opts)
  