%import json
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>sharedocapptest</title>
</head>
<body>
  <!-- link rel="stylesheet" href="http://twitter.github.com/bootstrap/assets/css/bootstrap-1.1.1.min.css" -->
  <link rel="stylesheet" href="/static/css/bootstrap-1.1.1.min.css">
  <style>
	.file-container {
		position:relative;
		}
		.file-container .file-view {
			width:64px;
			height:64px;
			position:absolute;
			}
			.file-container .file-view .delete {
				cursor: pointer;
				position: absolute;
				right: 0px;
				top: 0px;
			}
	.pile-view {
		
	}
  </style>

	
  <!-- script src="https://ajax.googleapis.com/ajax/libs/jquery/1.6.1/jquery.min.js"></script>
  <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js" type="text/javascript"></script>
  <script src="http://ajax.cdnjs.com/ajax/libs/json2/20110223/json2.js"></script>
  <script src="http://ajax.cdnjs.com/ajax/libs/underscore.js/1.1.6/underscore-min.js"></script>
  <script src="http://ajax.cdnjs.com/ajax/libs/backbone.js/0.3.3/backbone-min.js"></script -->

  <script src="/static/js/jquery.min.js" type="text/javascript"></script>
  <script src="/static/js/jquery-ui.min.js" type="text/javascript"></script>
  <script src="/static/js/jquery.iframe-transport.js" type="text/javascript"></script>
  <script src="/static/js/jquery.fileupload.js" type="text/javascript"></script>
  <!-- script src="/static/js/jquery.fileupload-ui.js" type="text/javascript"></script-->
  <script src="/static/js/json2.js" type="text/javascript"></script>
  <!-- script src="/static/js/underscore-min.js" type="text/javascript"></script-->
  <script src="/static/js/underscore.js" type="text/javascript"></script>
  <!-- script src="/static/js/backbone-min.js" type="text/javascript"></script-->
  <script src="/static/js/backbone.js"></script>
  <script src="/static/js/sharedoc.js" type="text/javascript"></script>
  <script>
	$(function() {
		window.pile = new Pile({{pile}})
		pile.files.reset({{files}})
		pileview = new PileView({model:window.pile})
		$('body').append(pileview.el)
	})
  </script>
	
  <script type="text/template" id="file-tpl">
	<img class="delete" src="/static/img/delete.png" />
	<img class="icon download" src="<%= icon %>" width="64" style="width:64px" />
	<span><%= name %></span>
  </script>
</body>
</html>