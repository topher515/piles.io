%import json
%from utils import m2j, ms2js
%from settings import APP_DOMAIN
%from api import Store


%def head():
  <link rel="stylesheet" type="text/css" href="/static/css/app.css">
  <script src="/static/js/piles.app.js" type="text/javascript"></script>
%end


%def content():
  <script>
	$(function() {
        // Set PilesIO defaults
		PilesIO.App = {{m2j(app_meta)}}
		var pilename = location.hash.slice(1)
		
		if (!pilename) window.location.href = "http://{{app_meta['APP_DOMAIN']}}/"
		
		var error = function(data) {
		    $('#brokescript').remove()
	        $('body').append('<h1>Not a valid pile: '+pilename+'</h1>')
		}
		
		$.ajax('http://'+PilesIO.App.APP_DOMAIN+'/piles?name='+pilename+'&callback=?',{
		    dataType:'jsonp',
		    success: function(data) {
		        if (!data) {
		            error()
		            return;
		        }
		        window.pile = new PilesIO.Pile(data[0])
		        window.pile.files.fetch({success: function() {
		            window.pileview = new PilesIO.PileView({model:window.pile})
            		$('body').append(pileview.render().el)
            		$('#brokescript').remove()
		            
		        }})  
		    },
		    error: error,
		})
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
	<span class="file-name" name="<%= name.toLowerCase() %>"><%= PilesIO.insert_spacers(name) %></span>
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
	
	<div class="searcher">
	    <form action="#">
	        <input class="input xlarge" type="text" value="Search Files" />
	    </form>
	</div>
		
	<div class="usage-container">
    	<div class="usage-small">
    		<span class="usage-sto"><%= human_size(usage_sto) %></span>
    	</div>
    	<div class="usage-big good">
    		<a href="/<%= name %>/usage">
    		    <img src="/static/img/box_xsmall.png" />
    			<span class="usage-sto"><%= human_size(usage_sto) %></span><br>
        		<img src="/static/img/arrow_up_xsmall.png" />
        		<span class="usage-put"><%= human_size(usage_put) %></span><br>
        		<img src="/static/img/arrow_down_xsmall.png" />
        		<span class="usage-get"><%= human_size(usage_get) %></span>
             </a>
		
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
				<p>Anyone can view and download the files you put here! <a href="http://{{APP_DOMAIN}}/<%= name %>?public=Yes">Check out your Pile's<!--'--> public view!</a></p>
			</div>
			
			<div class="trash">
				<img src="/static/img/trash.png" />
			</div>
			
		</div>

	</div>
  </script>

	<script type="text/template" id="notify-tpl">
		<a class="close" href="#">&#xd7;</a>
		<p><%= message %></p>
	</script>

	<script type="text/template" id="modal-tpl">
		<div class="modal-header">
			<h3><%= name %></h3>
				<a href="#" class="close">&times;</a>
			</div>
		<div class="modal-body">
	
			<img class="icon" src="<%= get_icon(ext) %>" />
			<ul>
				<li>Size: <%= human_size(size) %></li>
				<li>Type: <%= type %></li>
				<!-- --><% if (pub) {%>
				    <li>Public URL: <a href="http://<%= PilesIO.App.CONTENT_DOMAIN %>/<%= path %>">http://<%= PilesIO.App.CONTENT_DOMAIN %>/<%= path %></a></li>
				<!-- --><% } %>
			</ul>
		</div>
		<div class="modal-footer">
			<a href="#" class="btn close">Close</a>
			<a href="http://<%= PilesIO.App.APP_DOMAIN %>/piles/<%= pid %>/files/<%= id %>/content" class="btn primary">Download</a>
		</div>
	</script>

    <script type="text/template" id="twipsy-tpl">
        <div class="twipsy-arrow"></div>
        <div class="twipsy-inner"><%= tip %></div>
    </script>


  <div id="brokescript">
  	<img class="watermark" src="/static/img/pile_256.png" />
  </div>
  <noscript>Piles only works when Javascript is turned on!</noscript>

%end
  
%rebase layout content=content, head=head, meta={'title':'Test'}, app_meta=app_meta