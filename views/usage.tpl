%from utils import m2j, ms2js
%from settings import settings

%def head():
<link rel="stylesheet" href="http://{{settings('CONTENT_DOMAIN')}}/static/css/usage.css">
<script src="http://{{settings('CONTENT_DOMAIN')}}/static/js/highcharts.js" type="text/javascript"></script>
<!-- script src="http://{{settings('CONTENT_DOMAIN')}}/static/js/highcharts.theme-gray.js" type="text/javascript"></script -->
<script src="http://{{settings('CONTENT_DOMAIN')}}/static/js/piles.app.js" type="text/javascript"></script>
<script src="http://{{settings('CONTENT_DOMAIN')}}/static/js/piles.usage.js" type="text/javascript"></script>

%end

%def content():

<script>
$(function() {
    
    window.usage = new PilesIO.Usage({
        usage_total_put: {{usage_total_put['size']}},
        usage_total_get: {{usage_total_get['size']}},
        storage_total: {{storage_total['size']}}
    });
    
    usage.files.reset({{ms2js(files)}})
    
    usage.daily_puts.reset(({{ms2js(usage_dailies_puts)}}))
    usage.daily_gets.reset(({{ms2js(usage_dailies_gets)}}))
    usage.daily_sto.reset(({{ms2js(storage_dailies)}}))
    
    usageview = new PilesIO.UsageView({model:usage})
    $('.content').append(usageview.render().el)
    $('#noscript').remove()
});
</script>


<script type="text/template" id="usage-event-tpl">
    <td><%= datetime %></td><td><%= key.slice(14) %></td><td><%= human_size(bytes || objectsize) %></td>
</script>


<script type="text/template" id="usage-tpl">
    <div class="simple-usage">
    
        <div class="simple-item well" id="simple-usage-get">
            <h6>Downloads</h6>
            <h1>$<%= PilesIO.cost_calculator(usage_cost_get,usage_total_get).toFixed(3) %></h1>
            <h6><%= PilesIO.human_size(usage_total_get)%></h6>
        </div>
        <div class="simple-spacer" ><h6>+</h6></div>
        <div class="simple-item well" id="simple-usage-put">
            <h6>Uploads</h6>
            <h1>$<%= PilesIO.cost_calculator(usage_cost_put,usage_total_put).toFixed(3) %></h1>
            <h6><%= PilesIO.human_size(usage_total_put)%></h6>
        </div>
        <div class="simple-spacer" ><h6>+</h6></div>
        <div class="simple-item well" id="simple-storage">
            <h6>Storage</h6>
            <h1>$<%= PilesIO.cost_calculator(storage_cost,storage_total).toFixed(3) %></h1>
            <h6><%= PilesIO.human_size(storage_total) %></h6>
        </div>
        <div class="simple-spacer "><h6>=</h6></div>
        <div class="simple-item well" id="simple-sum">
            <h6>Total</h6>
            <h1>$<%= Number(PilesIO.cost_calculator(usage_cost_get,usage_total_get).toFixed(3)) + Number(PilesIO.cost_calculator(usage_cost_put,usage_total_put).toFixed(3)) + Number(PilesIO.cost_calculator(storage_cost,storage_total).toFixed(3)) %></h1>
        </div>
    </div>

    <div id="details-container">

            <!-- STORAGE -->
            <div id="detailed-storage" style="display:block;" class="details well">
            
                <div class="left">
                    <h2>Currently Stored</h2>
                    <br><%= PilesIO.human_size(storage_total) %>
                    <br>$<%= PilesIO.cost_calculator(storage_cost,storage_total).toFixed(3) %> per month
                     
                    <div class="pile">
                        <img src="http://{{settings('CONTENT_DOMAIN')}}/static/img/pile_256.png">
                    </div>
                </div>
                <div class="right">
                    <div id="sto-pie"></div>
                    <div id="sto-chart"></div>
                </div>
            </div>
        
            <!-- DOWNLOADS -->
            <div id="detailed-usage-get" class="details well">
                <div class="left">
                    <h2>Downloaded</h2>
                    <br><%= PilesIO.human_size(usage_total_get) %>
                     <br>$<%= PilesIO.cost_calculator(usage_cost_get,usage_total_get).toFixed(3) %> total
     
                     <div class="world">
                         <img class="arrow" src="http://{{settings('CONTENT_DOMAIN')}}/static/img/arrow_down.png">
                         <img class="graphic" src="http://{{settings('CONTENT_DOMAIN')}}/static/img/world_big.png">

                     </div>
                </div>
                <div class="right">
                    <div id="get-chart"></div>
                </div>
            </div>
            
            <!-- UPLOADS -->
            <div id="detailed-usage-put" class="details well">
                <div class="left">
                    <h2>Uploaded</h2>
                    <br><%= PilesIO.human_size(usage_total_put) %> 
                    <br>$<%= PilesIO.cost_calculator(usage_cost_put,usage_total_put).toFixed(3) %> total

                    <div class="comp" >
                        <img class="arrow" src="http://{{settings('CONTENT_DOMAIN')}}/static/img/arrow_up.png">
                        <img class="graphic" src="http://{{settings('CONTENT_DOMAIN')}}/static/img/macbook_pro.png" >

                    </div>  
                </div>
                <div class="right">
                    <div id="put-chart"></div>
                </div>
            </div>
    </div>
</script>


<div class="container">
    <div class="content" style="position:relative">
        
    
    <h1 style="margin: 25px inherit 0px inherit; z-index: 250;">
        <a class="btn" href="http://{{settings('CONTENT_DOMAIN')}}/app#{{pile['name']}}">&lt; Back</a>
        {{pile['name']}}</h1>

    <div>
        <p></p>
    </div>

    <div id="noscript" style="margin: 300px;">Bro, your javascript is off or broke!</div>

    </div>
</div>

%include feedback

%end

%rebase layout content=content, head=head, meta={'title':'Usage'}