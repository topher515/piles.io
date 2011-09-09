%from s3piles import public_get_url
%from utils import human_size

%def head():
<script src="/static/js/jquery.tablesorter.js"></script>
<script>
$(function() {
	$('table#pub-files').tablesorter({ sortList: [[1,0]] });
});
</script>
%end

%def content():
<div class="container">
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
	<table id="pub-files" class="zebra-striped">
		<thead>
			<tr>
				<td>Name</td><td>Size</td><td>Download</td><td>Torrent</td>
			</tr>
		</thead>
		%for file in files:
		<tbody>
			<tr>
				<td>{{file['name']}}</td>
				<td>{{human_size(file['size'])}}</td>
				<td><a class="btn primary small" href="{{public_get_url(file['path'])}}">Download</a></td>
				<td><a class="btn small" href="{{public_get_url(file['path'])}}?torrent">Torrent</a></td>
			</tr>
		</tbody>
		%end
	</table>
	%end
</div>
</div>
%end

%rebase layout content=content, head=head, meta={'title':pile['name']+' Public'}