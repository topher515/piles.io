%def dummy():
	<!-- Empty Block -->
%end

%def content():
<div class="content">
	<form action="/login" method="post">
		<div class="clearfix">
			<input class="xlarge" name="email" size="30" type="text" value="{{ email if email else 'Username' }}" >
			<input class="xlarge" name="password" size="30" type="password" value="Password" >
			<input type="submit" href="#" class="go btn primary" value="Go!" />
		</div>
	</form>
</div>
%end

%rebase layout content=content, style=dummy