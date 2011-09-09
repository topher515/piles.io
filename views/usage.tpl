%from utils import m2j, ms2js

%def head():
<link rel="stylesheet" href="/static/css/usage.css">
<script src="/static/js/highcharts.js" type="text/javascript"></script>
<!-- script src="/static/js/highcharts.theme-gray.js" type="text/javascript"></script -->
<script src="/static/js/piles.app.js" type="text/javascript"></script>
<script src="/static/js/piles.usage.js" type="text/javascript"></script>

%end

%def content():

<script>
$(function() {
	var pilehash = {{m2j(pile)}}
	var usage = new PilesIO.Usage({
		sto_total_bytes: pilehash.usage_sto,
		get_total_bytes: pilehash.usage_put,
		put_total_bytes: pilehash.usage_get,
	});
	usage.files.reset({{ms2js(files)}})
	usageview = new PilesIO.UsageView({model:usage})
	$('.content').append(usageview.render().el)
	$('#noscript').remove()
});
</script>

<script type="text/template" id="old-usage-tpl">


	<div class="comp" >
		<img class="arrow" src="/static/img/arrow_up.png">
		<img class="graphic" src="/static/img/macbook_pro.png" >
		<!-- h2>Uploads</h2 -->
		<div class="help-block">
			Files you and other users have uploaded to your Pile.
		</div>
	</div>

	<div class="sto-chart-container">
		<img src="/static/img/pile_256.png">
		<div id="sto-chart"></div>
	</div>
	<div class="world">
		<img class="arrow" src="/static/img/arrow_down.png">
		<img class="graphic" src="/static/img/world_big.png">
		<!-- h2>Downloads</h2 -->
		<div class="help-block">human_size(usage_put)
			Private files you or other users have downloaded. Or public files that anyone has downloaded.
		</div>
	</div>
	

</script>

<script type="text/template" id="usage-tpl">
	<table class="zebra-striped">
		<thead>
			<tr>
				<td></td><td>Total</td><td>Status</td><td></td>
			</tr>
		</thead>
		<tbody>
			<tr>
				<td>
					<div class="world">
						<img class="arrow" src="/static/img/arrow_down.png">
						<img class="graphic" src="/static/img/world_big.png">

					</div>
				</td>
				<td>Downloaded from Pile
				    <br><%= PilesIO.human_size(get_total_bytes) %>
				     <br>$<%= PilesIO.cost_calculator(cost_get,get_total_bytes).toFixed(3) %> total
				</td>
				<td></td>
				<td></td>
			</tr>
			<tr>
				<td>
					<div class="comp" >
						<img class="arrow" src="/static/img/arrow_up.png">
						<img class="graphic" src="/static/img/macbook_pro.png" >

					</div>	
				</td>
				<td>Uploaded to Pile
				    <br><%= PilesIO.human_size(put_total_bytes) %> 
    			    <br>$<%= PilesIO.cost_calculator(cost_put,put_total_bytes).toFixed(3) %> total
			    </td>
				<td></td>
				<td></td>
			</tr>
			<tr>
				<td>
					<div class="pile">
						<img src="/static/img/pile_128.png">
					</div>
				</td>
				<td>Stored in Pile
				    <br><%= PilesIO.human_size(sto_total_bytes) %>
				     <br>$<%= PilesIO.cost_calculator(cost_sto,sto_total_bytes).toFixed(3) %> per month
				</td>
				<td>
					<div id="sto-chart"></div>
				</td>
				<td></td>
			</tr>
		</tbody>
		
	</table>
</script>


<div class="container">
	<div class="content" style="position:relative">
		
	<img style="position:absolute; top:0; right:0; opacity:.1; z-index:200;" src="/static/img/pile_256.png" />
	<h1 style="margin: 25px inherit 0px inherit; z-index: 250;">
        <a class="btn" href="/{{pile['name']}}">&lt; Back</a>
        {{pile['name']}} | Usage Statistics</h1>

	<div id="noscript" style="margin: 300px;">Bro, your javascript is off or broke!</div>

	</div>
</div>

%include feedback

%end

%rebase layout content=content, head=head, meta={'title':'Usage'}