
%def head():
	<style>
	.login {
		margin-top: 250px;
	}
	</style>
%end

%def content():
<div class="content">
	<form class="login" action="/login" method="post">
		<div class="clearfix">
			<input class="xlarge" name="email" size="30" type="text" value="{{ email if email else 'Email' }}">
			<input class="xlarge" name="password" size="30" type="password" value="Password" >
			<input type="submit" class="go btn primary" value="Go!" />
		</div>
		<ul>
		</ul>
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