%from settings import settings

<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Piles | Alpha</title>

  <link rel="shortcut icon" href="http://{{settings('CONTENT_DOMAIN')}}/static/img/pile_32.png">

  <!-- link rel="stylesheet" href="http://twitter.github.com/bootstrap/assets/css/bootstrap-1.1.1.min.css" -->
  <link rel="stylesheet" type="text/css" href="http://{{settings('CONTENT_DOMAIN')}}/static/css/bootstrap-1.1.1.min.css">
  <link rel="stylesheet" type="text/css" href="http://{{settings('CONTENT_DOMAIN')}}/static/css/jquery-ui-1.8.16.custom.css">

  <!-- script src="https://ajax.googleapis.com/ajax/libs/jquery/1.6.1/jquery.min.js"></script>
  <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js" type="text/javascript"></script>
  <script src="http://ajax.cdnjs.com/ajax/libs/json2/20110223/json2.js"></script>
  <script src="http://ajax.cdnjs.com/ajax/libs/underscore.js/1.1.6/underscore-min.js"></script>
  <script src="http://ajax.cdnjs.com/ajax/libs/backbone.js/0.3.3/backbone-min.js"></script -->

  <script src="http://{{settings('CONTENT_DOMAIN')}}/static/js/jquery.min.js" type="text/javascript"></script>
  <script src="http://{{settings('CONTENT_DOMAIN')}}/static/js/jquery-ui.min.js" type="text/javascript"></script>
  <script src="http://{{settings('CONTENT_DOMAIN')}}/static/js/jquery.iframe-transport.js" type="text/javascript"></script>
  <script src="http://{{settings('CONTENT_DOMAIN')}}/static/js/jquery.fileupload.js" type="text/javascript"></script>
  <script src="http://{{settings('CONTENT_DOMAIN')}}/static/js/jquery.blockUI.js" type="text/javascript"></script>
  <!-- script src="http://{{settings('CONTENT_DOMAIN')}}/static/js/jquery.fileupload-ui.js" type="text/javascript"></script-->
  <script src="http://{{settings('CONTENT_DOMAIN')}}/static/js/json2.js" type="text/javascript"></script>
  <!-- script src="http://{{settings('CONTENT_DOMAIN')}}/static/js/underscore-min.js" type="text/javascript"></script-->
  <script src="http://{{settings('CONTENT_DOMAIN')}}/static/js/underscore.js" type="text/javascript"></script>
  <!-- script src="http://{{settings('CONTENT_DOMAIN')}}/static/js/backbone-min.js" type="text/javascript"></script-->
  <script src="http://{{settings('CONTENT_DOMAIN')}}/static/js/backbone.js"></script>
  <script>
$(function() {
    // Handle input focus and blur
    $(':input[title]').live('focus',function() {
        var $this = $(this)
        if($this.val() === $this.attr('title')) {
          $this.val('');
        }
    }).live('blur',function() {
        var $this = $(this)
        if($this.val() === '') {
          $this.val($this.attr('title'));
        }
    });
    $('a[href=#]').live('click',function(e) {
        e.preventDefault()
    })
})
  </script>
</script>


%head()

  <style>
	.top-right {
		position: absolute;
		top:8px;
		right:8px;
		z-index:1000;
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

<div class="top-right">
	<a href="http://{{settings('APP_DOMAIN')}}/logout">Logout</a>
</div>

	%content()
	
    %include feedback
	
</body>
</html>