%import json

%def head():
  <style>

	.file-view {
		width:72px;
		height:72px;
		position:absolute;
		display:block;
		}
		.file-view .working {
			display:none;
		}
		.file-view .progressbar {
			height: 5px;
		}
		.file-view .delete {
			cursor: pointer;
			position: absolute;
			right: -12px;
			top: 0px;
		}
		.file-view .icon-display {
			position:relative;
			}
			.file-view .icon-display > .ext {
				position: absolute;
				margin: auto;
				width: auto;
				top: 25px;
				left: 7px;
				font-size: 1.9em;
			}
		.file-view.working .working{
			display:block;
			position:absolute;
		}
	.pile-view {
		position:relative;
		margin: 45px auto;
		max-width:800px;
		}
		.pile-view .file-collection {
			min-height:500px;
			min-width: 600px;
		}
  </style>
%end


%def content():
  <script>
	$(function() {
		window.pile = new Pile({{pile}})
		pile.files.reset({{files}})
		pileview = new PileView({model:window.pile})
		$('body').append(pileview.el)
		$('#noscript').remove()
	})
  </script>
	
  <script type="text/template" id="file-tpl">
	<img class="delete" src="/static/img/delete.png" />
	<div class="icon-display  download" alt="Double click to download">
		<div class="ext"><%= ext %></div>
		<img class="working" src="/static/img/loading.gif" />
		<img class="icon" src="<%= icon %>" width="64" style="width:64px" />
	</div>
	<div class="progressbar"></div>
	<span><%= name %></span>
  </script>

  <script type="text/template" id="pile-tpl">
	<h1>Your Pile</h1>
	<h6><%= emails %></h6>
	<div class="file-collection well"></div>
  </script>

  <div id="noscript" style="margin: 300px;">Bro, your javascript is off or broke!</div>
%end
  
%rebase layout content=content, head=head