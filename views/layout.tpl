<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Piles Alpha | {{meta.get('title')}}</title>

  <link rel="shortcut icon" href="/static/img/pile_32.png">

  <!-- link rel="stylesheet" href="http://twitter.github.com/bootstrap/assets/css/bootstrap-1.1.1.min.css" -->
  <link rel="stylesheet" href="/static/css/bootstrap-1.1.1.min.css">
  <link rel="stylesheet" href="/static/css/jquery-ui-1.8.16.custom.css">

  <!-- script src="https://ajax.googleapis.com/ajax/libs/jquery/1.6.1/jquery.min.js"></script>
  <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js" type="text/javascript"></script>
  <script src="http://ajax.cdnjs.com/ajax/libs/json2/20110223/json2.js"></script>
  <script src="http://ajax.cdnjs.com/ajax/libs/underscore.js/1.1.6/underscore-min.js"></script>
  <script src="http://ajax.cdnjs.com/ajax/libs/backbone.js/0.3.3/backbone-min.js"></script -->

  <script src="/static/js/jquery.min.js" type="text/javascript"></script>
  <script src="/static/js/jquery-ui.min.js" type="text/javascript"></script>
  <script src="/static/js/jquery.iframe-transport.js" type="text/javascript"></script>
  <script src="/static/js/jquery.fileupload.js" type="text/javascript"></script>
  <script src="/static/js/jquery.blockUI.js" type="text/javascript"></script>
  <!-- script src="/static/js/jquery.fileupload-ui.js" type="text/javascript"></script-->
  <script src="/static/js/json2.js" type="text/javascript"></script>
  <!-- script src="/static/js/underscore-min.js" type="text/javascript"></script-->
  <script src="/static/js/underscore.js" type="text/javascript"></script>
  <!-- script src="/static/js/backbone-min.js" type="text/javascript"></script-->
  <script src="/static/js/backbone.js"></script>

</script>


%head()

  <style>
	.top-right {
		position: absolute;
		padding: 15px;
		top:0px;
		right:0px;
	}
	.small-center {
		width:400px;
		margin:250px auto;
	}
	.alert-message p, .alert-message a {
		margin: 0 1em;
	}
  </style>

</head>
<body>

	<div class="container">
		<div class="top-right">
			<a href="/logout">Logout</a>
		</div>
	%content()
	</div>
	<!-- div style="position:fixed; top:0; left:50%; color:white; box-shadow: 2px 2px 2px #888; background-color:#CCD; padding:5px 8px; border-radius: 0 0 5px 5px;">Feedback & Support
	</div -->
</body>
</html>