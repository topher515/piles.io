%from api import Store #public_get_url
%from utils import human_size
%from settings import settings

%def head():
<script>
$(function() {
    
    
    
});
</script>
%end

%def content():
<div class="container" style="z-index:600;">
<div class="content" style="position:relative;">
	
	<img style="position:absolute; top:-90px; right:-30px; opacity:.1;" src="http://{{settings('CONTENT_DOMAIN')}}/static/img/pile_256.png"  />
	<h1 style="margin: 25px inherit 0px inherit">Feedback</h1>
	%if feedbacks.count() == 0:
	<div>
		<h6>Nobody has left any feedback.</h6>
	</div>
	%else:
	
	<h6>These messages were left by other Alpha testers.</h6>
	<table id="pub-files" class="tablesorter zebra-striped">
		<thead>
			<tr>
				<th></th><th>Email</th><th>Message</th><th>When</th>
			</tr>
		</thead>
		%for feedback in feedbacks:
		<tbody>
			<tr>
				<td>
				    %if feedback['type'] == 'dislike':
				        <img src="http://{{settings('CONTENT_DOMAIN')}}/static/img/thumb_dislike_big.png" height="64"/>
				    %elif feedback['type'] == 'bug':
    				    <img src="http://{{settings('CONTENT_DOMAIN')}}/static/img/bug_big.png" height="64"/>
				    %else:
        			    <img src="http://{{settings('CONTENT_DOMAIN')}}/static/img/thumb_like_big.png" height="64"/>
				    %end
				</td>
				<td>{{feedback.get('email') or 'Anonymous'}}</td>
				<td>{{feedback['message']}}</td>
				<td>{{feedback['datetime'].strftime('%Y-%m-%d %H:%M:%S')}}</td>
			</tr>
		</tbody>
		%end
	</table>
	%end
</div>
</div>
%end

%rebase layout content=content, head=head, meta={'title':'Features'}