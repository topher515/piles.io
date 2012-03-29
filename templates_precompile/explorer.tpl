%import json
%from utils import m2j, ms2js
%from settings import settings


%def head():
    <link rel="stylesheet" type="text/css" href="/static/css/app.css">
	<link rel="stylesheet" href="/static/css/circle.skin/circle.player.css">
    <script type="text/javascript" src="/static/js/jquery.transform.js"></script>
    <script type="text/javascript" src="/static/js/jquery.grab.js"></script>
    <script type="text/javascript" src="/static/js/jquery.jplayer.js"></script>
    <script type="text/javascript" src="/static/js/mod.csstransforms.min.js"></script>
    <script type="text/javascript" src="/static/js/circle.player.js"></script>
    <script type="text/javascript" src="/static/js/piles.app.js" ></script>
    <script type="text/javascript" src="/static/js/piles.resample.js" ></script>
%end


%def content():
    <div class="modal-header">
		<h3><%= name %></h3>
			<a href="#" class="close">&times;</a>
		</div>
	<div class="modal-body">

%end
  
%rebase layout content=content, head=head, meta={'title':'Explorer Test'}, app_meta=app_meta