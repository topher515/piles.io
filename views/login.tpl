
%def head():

%end

%def content():
<div class="small-center">
	<form action="/login" method="post">
		<div class="clearfix">
			<h1>Piles (Alpha)</h1>
			<input class="xlarge" name="email" size="30" title="Email" type="text" value="{{ email }}">
			<input class="xlarge" name="password" size="30" title="Password" type="password" value="Password" >
			<input type="submit" class="go btn primary" value="Go!" />
			<div class="clearfix" style="margin-top:25px">
			<a href="/create">Do you have an invitation?</a>
			<p>Piles.io was built as an experiment and learning experience. 
				If you'd like to see what it's all about just <a href="mailto:ckwilcox@gmail.com"</a>ask Chris for 
				an invitation code.</a></p>
			
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

%rebase layout content=content, head=head, meta={'title':'Login'}