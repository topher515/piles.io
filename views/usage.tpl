
%def head():
<link rel="stylesheet" href="/static/css/usage.css">
<script src="/static/js/piles.usage.js" type="text/javascript"></script>
%end

%def content():

<script type="text/template" id="usage-tpl">
	
	<div class="comp" >
		<img class="arrow" src="/static/img/arrow_up.png">
		<img class="graphic" src="/static/img/macbook_pro.png" >
		<h2>Uploads</h2>
		<div class="help-block">
			Files you and other users have uploaded to your Pile.
		</div>
	</div>
	<div class="pile">
		<img src="/static/img/pile_256.png">
		<div class="help-block">
			
		</div>
	</div>
	<div class="world">
		<img class="arrow" src="/static/img/arrow_down.png">
		<img class="graphic" src="/static/img/world_big.png">
		<h2>Downloads</h2>
		<div class="help-block">human_size(usage_put)
			Private files you or other users have downloaded. Or public files that anyone has downloaded.
		</div>
	</div>

</script>
%end

%rebase layout content=content, head=head, meta={'title':'Usage'}