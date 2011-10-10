Socketbone = Socketbone || {};
console = console || {log:function() {}}


// parseUri 1.2.2
// (c) Steven Levithan <stevenlevithan.com>
// MIT License
// http://blog.stevenlevithan.com/archives/parseuri

function parseUri (str) {
	var	o   = parseUri.options,
		m   = o.parser[o.strictMode ? "strict" : "loose"].exec(str),
		uri = {},
		i   = 14;

	while (i--) uri[o.key[i]] = m[i] || "";

	uri[o.q.name] = {};
	uri[o.key[12]].replace(o.q.parser, function ($0, $1, $2) {
		if ($1) uri[o.q.name][$1] = $2;
	});

	return uri;
};

parseUri.options = {
	strictMode: false,
	key: ["source","protocol","authority","userInfo","user","password","host","port","relative","path","directory","file","query","anchor"],
	q:   {
		name:   "queryKey",
		parser: /(?:^|&)([^&=]*)=?([^&]*)/g
	},
	parser: {
		strict: /^(?:([^:\/?#]+):)?(?:\/\/((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?))?((((?:[^?#\/]*\/)*)([^?#]*))(?:\?([^#]*))?(?:#(.*))?)/,
		loose:  /^(?:(?![^:@]+:[^:@\/]*@)([^:\/?#.]+):)?(?:\/\/)?((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?)(((\/(?:[^?#](?![^?#\/]*\.[^?#\/.]+(?:[?#]|$)))*\/?)?([^?#\/]*))(?:\?([^#]*))?(?:#(.*))?)/
	}
};


Socketbone.Client = function(url,timeout) {
    
    var url = url,
        parsedUri = parseUri(url)
        socket = io.connect(url),
        syncEventCounter = 0,
        syncEventCallbacks = {},
        timeout = timeout ? timeout : 10000,
    
    socket.on('sync:success', function(resp, syncEventId) {
        syncEventCallbacks[syncEventId].success(resp)
        delete syncEventCallbacks[syncEventId]
    })
    
    socket.on('sync:error', function(resp, syncEventId) {
        syncEventCallbacks[syncEventId].error(resp)
        delete syncEventCallbacks[syncEventId]
    })
    
    socket.on('sync:ack', function(syncEventId) {
        delete syncEventCallbacks[syncEventId]
    })
    
    socket.on('connect', function() {
        console.log('Connected successfully!')
    })
    
    this.sync = function(method,model,options) {
        var uri = model.url instanceof Function ? model.url() : model.url;
        
        if (options.success || options.error) {
            var syncEventId = ''+syncEventCounter++
            syncEventOptions[syncEventId] = {
                success:options.success || function() {},
                error:options.error || function() {},
            }
        }
        
        socket.emit('sync', method, uri
            method == 'create' || method == 'update' ? model.toJSON() : null,
            syncEventId)

    }
}
