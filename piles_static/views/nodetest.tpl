<html>
<head>
	<!--script src="http://localhost:8030/socket.io/socket.io.js"></script-->
	<script src="http://cdn.socket.io/stable/socket.io.js"></script>
	<script src="http://code.jquery.com/jquery-1.5.1.min.js"></script>
	
	<style>
		body, input, textarea {
			font-size: 14px;
			font-family: helvetica, sans-serif;
		}
		
		#chat {
			width: 420px;
			margin: auto;
			padding-bottom: 150px;
		}
		#chat #me {			
			width: 100%;
			max-width: 420px;
			min-height: 1em;
			position: fixed;
			bottom: 125px;
			margin: auto;
		}
		#chat #sender {
			width: 100%;
			max-width: 420px;
			min-height: 100px;
			position: fixed;
			bottom: 15px;
			margin: auto;
		}
		#chat .message {
			width: 100%;
			max-width: 500px;
			min-height: 1em;
			padding: 3px;
			-webkit-border-radius: 5px;
			-moz-border-radius: 5px;
			border-radius: 5px;
			background-color: #F0F0F0;
			margin: 3px 0px;
		}
		
		#chat .message:before {
			content: '';
		}
		
		#chat .message .who {
			font-weight: 300;
		}
	</style>
	
	<script>
		var VERSION = 0.01;
		var COLORS = ['#FDC0C0','#C0FDC0','#C0C0FD','#FDFDC0','#C0FDFD','#FDC0FD'];
		var NAMES = ['bob','tim','billy','johnny',"Chris"];
	
		var whoswho = {}
	
		var socket = new io.Socket('localhost', {'port':8030});
		
		socket.connect();
		socket.on('connect', function() {});
		socket.on('message', function(msg) {
			receive(msg)
		});
		socket.on('disconnect', function() {
			add_msg('Info','Disconnected!')
			//socket.connect();
		});

		var wrap = function(who,msg,id) {
			if (id) id_str = ' session_' + id
			else id_str = ''
			
			if (id) {
				if (!whoswho[id]) {
					// We've never seen this session before
					$('<style> #chat .session_'+id+' { background-color: '
						+ COLORS[Math.floor(Math.random() * COLORS.length)]
						+'; }</style>').appendTo($('head'))
					whoswho[id] = who;
				} else if (whoswho[id] != who) {
					// The user of this session has changed his name
					$('.message.session_'+id+' who').html(who)
					whoswho[id] = who
				}
			}
			
			return $('<div class="message'+id_str+'"><span class="who">'+who+':</span> '+msg+'</div>')
		}
		var add_msg = function(who,msg,id) {
			$('#messages').append(wrap(who,msg,id));
			$('html, body').stop().animate({ 'scrollTop': $('#messages').height() }, 500);
		}

		var send = function(who,msg) {
			socket.send(JSON.stringify({
				'who':who,
				'msg':msg,
				'version':VERSION,
			}))
		}
		
		var receive = function(msg) {
			fromserver = JSON.parse(msg)
			add_msg(fromserver.who,fromserver.msg,fromserver.id)
			
		}

		$(function() {
			$('#sender').keypress(function(e) {
				if (e.which == 13) {
					msg = $(this).val()
					add_msg('Me',msg)
					send($('#me').val(),msg)
					$(this).val('')
				}
			});
			
			$('#me').val(NAMES[Math.floor(Math.random() * NAMES.length)])
			
		});
	</script>
</head>
<body>
	<div id="chat">
		<div id="messages">
			
		</div>
		<input id="me" type="text" value="">
		<textarea id="sender"></textarea>
	</div>
</body>
</html>