%def head():

%end

%def content():
<div class="small-center">
	<form action="/password" method="post">
		<div class="clearfix">
			<h1>Set Password</h1>
			%if code:
			<input type="hidden" name="code" value="{{code}}">
			%else:
			<label>Old Password:</label>
			<div class="clearfix"></div>
			<input class="xlarge" name="old_password" size="30" type="text" value="" >
			%end
			<label>New Password:</label>
			<div class="clearfix"></div>
			<input class="xlarge" name="new_password" size="30" type="password" value="" >
			<input type="submit" class="go btn primary" value="Go!" />
		</div>
		<ul>
		</ul>
	</form>
	%for error in errors:
		<div class="alert-message error">
			<a class="close" href="#">×</a>
			<p><strong>Error:</strong> {{!error}}</p>
		</div>
	%end
</div>
%end

%rebase layout content=content, head=head, meta={'title':'Change your password'}