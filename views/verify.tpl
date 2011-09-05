
%def head():

%end

%def content():
<div class="small-center">
	<form action="/verify" method="GET">
		<div class="clearfix">
			<h1>Verify Email</h1>
			<input class="xlarge" name="email" size="30" type="text" value="{{ email }}">
			<input class="xlarge" name="code" size="30" type="text" value="{{ code }}" >
			<input type="submit" class="go btn primary" value="Go!" />
		</div>
	</form>
	%for error in errors:
		<div class="alert-message error">
			<a class="close" href="#">×</a>
			<p><strong>Error:</strong> {{error}}</p>
		</div>
	%end
</div>
%end

%rebase layout content=content, head=head