window.ShinyBox or= {}


ShinyBox.onMessage = (message,origin)->
  

ShinyBox.setupXDM = (options)->
  # Setup `provider`--inner iframe document
  socket = new easyXDM.Socket onMessage: ShinyBox.onMessage
    
ShinyBox.bootstrap = (options)->
  ShinyBox.setupXDM()
    
Extern.bootstrap()
  
