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
    <table class="zebra-striped">
        <tbody>
            <!-- STORAGE -->
            <tr>
            
                <td><h4>In Pile</h4>
                    <br><%= PilesIO.human_size(storage_total) %>
                     <br>$<%= PilesIO.cost_calculator(storage_cost,storage_total).toFixed(3) %> per month
                     
                     
                         <div class="pile">
                             <img src="http://{{settings('CONTENT_DOMAIN')}}/static/img/pile_256.png">
                         </div>
                </td>
                <td>
                </td>
                <td>
                    <div id="sto-pie"></div>
                    <div id="sto-chart"></div>
                </td>
                <td></td>
            </tr>
        
            <!-- DOWNLOADS -->
            <tr class="download-row">
                <td>
                    <h3>Downloaded</h3>
                    <h6> from Pile</h6>
            
                    <h4>Total</h4>
                    <br><%= PilesIO.human_size(usage_total_get) %>
                     <br>$<%= PilesIO.cost_calculator(usage_cost_get,usage_total_get).toFixed(3) %> total
                     

                     
                </td>
                 
                <td>
                     <div class="world">
                         <img class="arrow" src="http://{{settings('CONTENT_DOMAIN')}}/static/img/arrow_down.png">
                         <img class="graphic" src="http://{{settings('CONTENT_DOMAIN')}}/static/img/world_big.png">

                     </div>
                </td>
                <td>
                    <table id="get-events">
                    </table>
                    <div id="get-chart"></div>
                </td>
                <td></td>
            </tr>
            
            <!-- UPLOADS -->
            <tr>
                <td><h3>Uploaded</h3>
                    <h6> to Pile</h6>
            
                    <h4>Total</h4>
                    <br><%= PilesIO.human_size(usage_total_put) %> 
                    <br>$<%= PilesIO.cost_calculator(usage_cost_put,usage_total_put).toFixed(3) %> total
                </td>
                <td>
                    <div class="comp" >
                        <img class="arrow" src="http://{{settings('CONTENT_DOMAIN')}}/static/img/arrow_up.png">
                        <img class="graphic" src="http://{{settings('CONTENT_DOMAIN')}}/static/img/macbook_pro.png" >

                    </div>  
                </td>
                <td>
                    <div id="put-chart"></div>
                </td>
                <td></td>
            </tr>
        </tbody>
        
    </table>
</script>


<div class="container">
    <div class="content" style="position:relative">
        
    <h1 style="margin: 25px inherit 0px inherit; z-index: 250;">
        <a class="btn" href="http://{{settings('CONTENT_DOMAIN')}}/app#{{pile['name']}}">&lt; Back</a>
        {{pile['name']}} | Usage Statistics</h1>

    <div>
        <p></p>
    </div>

    <div id="noscript" style="margin: 300px;">Bro, your javascript is off or broke!</div>

    </div>
</div>

%include feedback

%end

%rebase layout content=content, head=head, meta={'title':'Usage'}