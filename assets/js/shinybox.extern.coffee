window.ShinyBox or= {}

Extern = ShinyBox.Extern = {}

Extern.resize = (width,height)->
  el = document.getElementsById 'shinybox'
  el.style.width = parseInt(width) + 'px'
  el.style.height = parseInt(height) + 'px'

Extern.onMessage = (message,origin)->

Extern.bootstrap = (options)->
  # Setup `consumer`--container document
  socket = new easyXDM.Socket
    remote: options.remote
    onMessage: Extern.onMessage
    container: options.container
    props: 
      style: 
        border: "1px solid #DDD"
        width: '300px'
        height: '80px'

opts = {}
for key,val in (window._shiny or [])
  opts[key] = val
Extern.bootstrap(opts)
  