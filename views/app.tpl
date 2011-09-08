%import json
%from s3piles import public_get_url
%from utils import m2j, ms2js


%def head():
  <link rel="stylesheet" href="/static/css/app.css">
  <script src="/static/js/piles.app.js" type="text/javascript"></script>
%end


%def content():
  <script>
	$(function() {
		window.pile = new PilesIO.Pile({{m2j(pile)}})
		pile.files.reset({{ms2js(files)}})
		pileview = new PilesIO.PileView({model:window.pile})
		$('body').append(pileview.render().el)
		$('#noscript').remove()
	})
  </script>
	
  <script type="text/template" id="file-tpl">
	<img class="world-icon" src="/static/img/world.png" -->
	<!-- img class="delete" src="/static/img/delete.png" -->
	<div class="icon-display" alt="Double click to download">
		<!-- div class="ext"><%= ext %></div -->
		<img class="working" src="/static/img/loading.gif" />
		<img class="icon" src="<%= get_icon(ext) %>" height="48" />
		<img class="info" src="/static/img/info.png">
	</div>
	<div class="progressbar"></div>
	<span class="file-name"><%= name %></span>
  </script>

  <script type="text/template" id="email-tpl">
	<li><h6><%= email %></h6></li>
  </script>

  <script type="text/template" id="pile-tpl">
	
	<img class="watermark" src="/static/img/pile_256.png" />
	
	<div class="emails">
		<h6 class="current"><%= emails %></h6>
		<!-- input type="text" value="Email" /><button class="btn small">Add</button-->
	</div>
		
	<div class="usage">
		<a href="/<%= name %>/usage">
		<span class="usage-item extras">
			Up: <span class="usage-put"><%= human_size(usage_put) %></span>
		</span>
		<span class="usage-item extras">
		 	Down: <span class="usage-get"><%= human_size(usage_get) %></span>
		</span>
		<span class="usage-item">
			Storage: <span class="usage-sto"><%= human_size(usage_sto) %></span>
		</span>
		</a>
		
		<div class="twipsy below extras" style="top: 20px; left: 213px; ">
			<div class="twipsy-arrow"></div>
			<div class="twipsy-inner">Click for usage statistics</div>
		</div>
	</div>
		
	<div class="file-collection">
		<div class="private well">
			<!-- h1 class="pile-title">Private</h1 -->
			<h1 class="pile-title pile-name"><span><%= name %></span> <button class="btn small rename">Rename</button></h1>
			
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
		<div class="public well">
			<h1 class="pile-title">Public</h1>
			<div class="warning">
				<img src="/static/img/warning_48.png" />
				<p>Anyone can view and download the files you put here! <a href="/{{pile['name']}}?public=Yes">Check out your Pile's<!--'--> public view!</a></p>
			</div>
			
			<div class="trash">
				<h1 class="pile-title">Trash</h1>
				<img src="/static/img/trash.png" />
			</div>
			
		</div>

	</div>
  </script>

  <script type="text/template" id="notify-tpl">
		<a class="close" href="#">×</a>
		<p><%= message %></p>
  </script>

  <script type="text/template" id="modal-tpl">
	<div class="modal-header">
		<h3><%= name %></h3>
			<a href="#" class="close">×</a>
		</div>
	<div class="modal-body">
	
		<img class="icon" src="<%= get_icon(ext) %>" />
		<ul>
			<li>Size: <%= human_size(size) %></li>
			<li>Type: <%= type %></li>
			<li>Public URL: <% if (pub) {%><a href="http://piles.io/~<%= pid %>-<%= id %>">http://localhost:8080/~<%= pid %>-<%= id %></a><% } else { %>None<% } %></li>
		</ul>
	</div>
	<div class="modal-footer">
		<a href="#" class="btn close">Close</a>
		<a href="/piles/<%= pid %>/files/<%= id %>/content" class="btn primary">Download</a>
	</div>
  </script>


  <div id="noscript" style="margin: 300px;">Bro, your javascript is off or broke!</div>

  %include feedback

%end
  
%rebase layout content=content, head=head, meta={'title':pile["name"]}