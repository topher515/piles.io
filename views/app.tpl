%import json

%def head():
  <style>
	.alert-message {
		position:fixed;
		width: 80%;
		border-top-left-radius:0;
		border-top-right-radius:0;
	}
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
			right: -13px;
			top: 0;
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
	.file-view.working {
		opacity: .7;
	}
	.pile-view {
		position:relative;
		margin: 45px auto;
		max-width:800px;
		}
		.pile-view .file-collection {

		}
		.pile-view .private {
			min-height:400px;
			width: 800px;
			margin:0;
			padding:0;
		}
		.pile-view .private.drophover {
			background-color:#CCC;
		}
		.pile-view .public {
			margin: 0;
			height:150px;
			width: 642px;
			background-color:#EED;
			display:inline-block;
			padding:0;
		}
		.pile-view .public.drophover {
			background-color:#DDA;
		}
		.pile-view .trash {
			margin:0;
			height:150px;
			width:150px;
			background-color:#EDD;
			display:inline-block;
			padding:0;
		}
		.pile-view .trash.drophover {
			background-color:#DAA;
		}
		
		.pile-view .well {
			position:relative;
		}
		.pile-view .pile-title {
			position:absolute;
			top:.3em;
			left:.3em;
			opacity: .5;
		}
  </style>
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
	<!-- img class="delete" src="/static/img/delete.png" -->
	<div class="icon-display  download" alt="Double click to download">
		<div class="ext"><%= ext %></div>
		<img class="working" src="/static/img/loading.gif" />
		<img class="icon" src="<%= icon %>" width="64" style="width:64px" />
	</div>
	<div class="progressbar"></div>
	<span><%= name %></span>
  </script>

  <script type="text/template" id="pile-tpl">
	<h6><%= emails %></h6>
	<div class="file-collection">
		<div class="private well">
			<h1 class="pile-title">Private</h1>
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