%import json

%def head():
  <link rel="stylesheet" href="/static/css/app.css">
%end


%def content():
  <script>
	$(function() {
		window.pile = new Pile({{pile}})
		pile.files.reset({{files}})
		pileview = new PileView({model:window.pile})
		$('.container').append(pileview.el)
		$('#noscript').remove()
	})
  </script>
	
  <script type="text/template" id="file-tpl">
	<img class="world-icon" src="/static/img/world.png" -->
	<!-- img class="delete" src="/static/img/delete.png" -->
	<div class="icon-display download" alt="Double click to download">
		<div class="ext"><%= ext %></div>
		<img class="working" src="/static/img/loading.gif" />
		<img class="icon" src="<%= icon %>" width="64" style="width:64px" />
	</div>
	<div class="progressbar"></div>
	<span class="file-name"><%= name %></span>
  </script>

  <script type="text/template" id="pile-tpl">
	<h1 class="pile-name">Piles | <span><%= name %></span> <button class="btn small rename">Rename</button></h1>
	<h6><%= emails %></h6>
		
	<div class="file-collection">
		<div class="private well">
			<h1 class="pile-title">Private</h1>
			<div class="popover left help">
				<div class="arrow"></div>
				<div class="inner">
					<h3 class="title">Drag files on to me!</h3>
					<div class="content">
						<p>Grab files from anywhere and drag them onto this window! They'<!--'-->ll Auto-magically upload to our systems.</p>
					</div>
				</div>
			</div>
		</div>
		<div class="bottom-container">
			<div class="public well">
				<h1 class="pile-title">Public</h1>
			</div>
			<div class="trash well">
				<h1 class="pile-title">Trash</h1>
			</div>
		</div>
	</div>
  </script>

  <script type="text/template" id="notify-tpl">
		<a class="close" href="#">×</a>
		<p><%= message %></p>
  </script>


  <div id="noscript" style="margin: 300px;">Bro, your javascript is off or broke!</div>
%end
  
%rebase layout content=content, head=head