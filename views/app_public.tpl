%from api import Store #public_get_url
%from utils import human_size
%from settings import settings

%def head():
<script src="/static/js/jquery.tablesorter.js"></script>
<script>
$(function() {
	$('table#pub-files').tablesorter();
});
</script>
%end

%def content():
<div class="container" style="z-index:600;">
<div class="content" style="position:relative;">
	
	<img style="position:absolute; top:-90px; right:-30px; opacity:.1;" src="/static/img/pile_256.png"  />
	<h1 style="margin: 25px inherit 0px inherit">
	    %if authenticated:
	    <a class="btn" href="/{{pile['name']}}">&lt; Back</a>
	    %end
	    {{pile['name']}} 
	    %if authenticated:
	        | Public Files
	    %end
	</h1>
	<h6>These are the files that this Pile's users have shared with the public.</h6>
	%if len(files) == 0:
	<div>
		<p>The users of this pile haven't shared any files.</p>
	</div>
	%else:
	<table id="pub-files" class="tablesorter zebra-striped">
		<thead>
			<tr>
				<th>Name</th><th>Size</th><th>Download</th><th>Torrent</th>
			</tr>
		</thead>
		%for file in files:
		<tbody>
			<tr>
				<td>{{file['name']}}</td>
				<td>{{human_size(file['size'])}}</td>
				<td><a class="btn primary small" href="http://{{settings('APP_DOMAIN')}}/~{{file['pid']}}-{{file['fid']}}">Download</a></td>
				<td><!-- a class="btn small" href="{{Store().public_get_url(file['path'])}}?torrent" -->Torrent</a></td>
			</tr>
		</tbody>
		%end
	</table>
	%end
</div>
</div>
%end

%rebase layout content=content, head=head, meta={'title':pile['name']+' Public'}