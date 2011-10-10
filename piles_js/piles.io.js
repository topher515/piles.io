exports = exports || {};

var socket_io = require("socket.io")
,   _ = require('underscore')
,   connect = require('connect')

,   auth = require('auth.tjs')
,   db = require('db.tjs')
,   socketbone = require('socketbone')
;


    
// Setup the app
exports.listen = function(app) {
      
    socket = socket_io.listen(app);
    socketboner = socketbone.listen(socket)
    
    
    socketboner.on('/piles/:pid','read', function(pid, responder) {
        var pile; await {
            pile = db.collection('piles').findOne({pid:pid})
        }
        
    })
    
    socket.on('connection', function(client) {
        client.emit()
    })
    
    socket.set('authorization', function(data,accept) {
        if (data.headers.cookie) {
            data.cookie = connect.utils.parseCookie(data.headers.cookie);
            data.sessionId = data.cookie
        } else {
            return accept('No cookie found.', false)
        }
    })
    
}