var socket_io = require('socket.io')

/**
 * Normalize the given path string,
 * returning a regular expression.
 *
 * An empty array should be passed,
 * which will contain the placeholder
 * key names. For example "/user/:id" will
 * then contain ["id"].
 *
 * @param  {String|RegExp} path
 * @param  {Array} keys
 * @param  {Boolean} sensitive
 * @param  {Boolean} strict
 * @return {RegExp}
 * @api private
 */

function normalize(path, keys, sensitive, strict) {
  if (path instanceof RegExp) return path;
  path = path
    .concat(strict ? '' : '/?')
    .replace(/\/\(/g, '(?:/')
    .replace(/(\/)?(\.)?:(\w+)(?:(\(.*?\)))?(\?)?/g, function(_, slash, format, key, capture, optional){
      keys.push({ name: key, optional: !! optional });
      slash = slash || '';
      return ''
        + (optional ? '' : slash)
        + '(?:'
        + (optional ? slash : '')
        + (format || '') + (capture || (format && '([^/.]+?)' || '([^/]+?)')) + ')'
        + (optional || '');
    })
    .replace(/([\/.])/g, '\\$1')
    .replace(/\*/g, '(.*)');
  return

Socketbone.Server = function(socket) {
    
    var self = this;
    
    function Responder(syncEventId) {
        var self = this;
        this.responded = false;
        this.success = function(resp) {
            self.responded = true
            socket.emit('sync:success',resp ? resp : '', syncEventId)
        }
        this.error = function(resp) {
            self.responded = true
            socket.emit('sync:error' ,resp ? resp : '', syncEventId)
        }
        this.ack = function() {
            self.responded = true
            socket.emit('sync:ack', syncEventId)
        }
    }


    
    this.on = function(pathSpec,method,resp) {
        
        var keys = [],
            pathRegex = normalize(psthSpec, keys)
            
        socket.on('sync', function(evmethod, path, model, syncEventId) {
            
            if (evmethod !== method) return
            
            var pathParams = pathRegex.exec(path)
            if (!pathParams) return
            
            var params = pathParams.slice(1),
                responder = (new Responser);
            params.push(responder)
            callback.apply(self, params)
            if (!responder.responded) {
                responder.ack() // If the path handler hasn't responded then we'll just send an ack ourselves
            }
        })
        
    }
    
}

