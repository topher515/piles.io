<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Piles Alpha</title>

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

  <!-- Begin Feedback -->
<script type="text/javascript">
reformal_wdg_domain    = "piles_io";
reformal_wdg_mode    = 0;
reformal_wdg_title   = "Piles.io";
reformal_wdg_ltitle  = "Bugs? Comments? Leave Feedback";
reformal_wdg_lfont   = "";
reformal_wdg_lsize   = "";
reformal_wdg_color   = "#FFA000";
reformal_wdg_bcolor  = "#516683";
reformal_wdg_tcolor  = "#FFFFFF";
reformal_wdg_align   = "left";
reformal_wdg_waction = 0;
reformal_wdg_vcolor  = "#9FCE54";
reformal_wdg_cmline  = "#E0E0E0";
reformal_wdg_glcolor  = "#105895";
reformal_wdg_tbcolor  = "#FFFFFF";

reformal_wdg_bimage = "52fd91ce34775cff4dd90673aff5b434.png";

</script>

<script type="text/javascript" language="JavaScript" src="http://idea.informer.com/tab6.js?domain=piles_io"></script><noscript><a href="http://piles_io.idea.informer.com">Piles.io feedback </a> <a href="http://idea.informer.com"><img src="http://widget.idea.informer.com/tmpl/images/widget_logo.jpg" /></a></noscript>

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
</body>
</html>