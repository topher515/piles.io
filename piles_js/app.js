// Imports
var tamejs = require("tamejs").register()
,    sys = require("sys")
,	express = require("express")
,   _ = require("underscore")

,   pio = require('piles.io')
,   settings = require('settings')
,   server = require('server.tjs')
;


/* 
 * APPLICATION SETUP 
 */


// Setup the express application 
app = express.createServer();
app.listen(7070);
app.use(expres.bodyParser());
app.use(express.cookieParser());
app.use(express.session({ secret: settings.SECRET_KEY }));
app.set('view engine','ejs')

pio.listen(app) // Start piles.io listening on this socket

server.register(app) // Add paths for page handling
