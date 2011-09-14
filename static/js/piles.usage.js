$(function() {
    
	window.PilesIO ? console.log('PilesIO already in global scope') : (function() {throw "Missing PilesIO library"})()
    
    /* Utilities */
    var text_shortener = PilesIO.text_shortener = function(str,max_len)  {
        if (str.length > max_len) {
            spot = str.length*.75
            too_long = str.length - max_len
            halfsies = too_long/2
            return str.slice(0,spot-halfsies-2)+'...'+str.slice(spot+halfsies+1)
        }
        return str
    }
    
    var cost_calculator = PilesIO.cost_calculator = function(cost_per_gb,total_bytes) {
        total_gbs = total_bytes / (1024*1024*1024)
        return total_gbs * cost_per_gb 
    }
    
    
    /* Models */
    var FileCollection = PilesIO.FileCollection = Backbone.Collection.extend({
		model: PilesIO.File,
		comparator:function(file) {
		    return -file.get('size')
		}
	})
    
    var UsageEvent = PilesIO.UsageEvent = Backbone.Model.extend({})
    var UsageEventCollection = PilesIO.UsageEventCollection = Backbone.Collection.extend({
        model:UsageEvent,
		comparator:function(uevent) {
		    return uevent.get('datetime')
		}
    })
    
    var Usage = PilesIO.Usage = Backbone.Model.extend({
        defaults: {
            sto_total_bytes:0,
            put_total_bytes:0,
            get_total_bytes:0,
            cost_sto:0.160,
            cost_get:0.140,
            cost_put:0.020,
        },
        initialize:function() {
    		this.files = new FileCollection
    		this.usage_gets = new UsageEventCollection
    		this.usage_puts = new UsageEventCollection
        },
    });
    
    
    /* Views */
    var UsageEventView = PilesIO.UsageEvent = Backbone.Model.extend({
        
        tagName: 'tr'
        
        initialize:function() {
            this.$el = $(this.el)
        },
        render:function() {
            this.$el.html(_.template($("#usage-event-tpl"),this.model.toJSON()))
        }
    })
    
    var UsageView = PilesIO.UsageView = Backbone.View.extend({
        
        className: 'usage-diagram',
        
        initialize: function() {

        },
        _chart_files:function(total,files) {
            var series = [],
                percent10 = total/10,
                cursorSize = total,
                cursor = 0;
            while (files[cursor] != undefined && cursorSize > percent10) {
                file = files[cursor]
                series.push([file.get('name'),file.get('size')])
                cursor += 1
                cursorSize -= file.get('size')
            }
            series.push(['Others...',cursorSize])
            return series;
        },
        
        animate_progressbar: function($pbar,to) {
            var step_pbar = function($pbar,at,to) {
                $pbar.progressbar( "option", "value",at)
                if (at < to) {
                    setTimeout(function() {step_pbar($pbar,at+1,to)}, 15);
                }
            }
            step_pbar($pbar,0,to)
        },
        render:function() {
            var $el = $(this.el),
                tpl = _.template($('#usage-tpl').html())
            $el.html(tpl(this.model.toJSON()))
            
            
            // Render the most recent event lists
            var $ges = $el.find('#get-events')
            var $pes = $el.find('#put-events')
            
            _.each(this.model.usage_gets.models, function(m) {
                $ges.append((new UsageEventView({model:m}).render().el))
            })
            _.each(this.model.usage_puts.models, function(m) {
                $pes.append((new UsageEventView({model:m}).render().el))
            })
            
            // Render The Storage chart
            var $usage_sto_chart = $el.find('#sto-chart')
            var data = this._chart_files(this.model.get('sto_total_bytes'),this.model.files.models)
            
            var chart = new Highcharts.Chart({
                chart: {
                    renderTo: $usage_sto_chart.get(0),
                    backgroundColor: 'transparent',
                    plotBorderWidth: null,
                    plotShadow: false,
                    style:{
                        fontFamily:$('body').css('font-family'),
                    },
                    width:600,
                    height:180,
                },
                legend: {
                    enabled:true,
                    labelFormatter: function() {
                        return 'fdgdsfs'
                    }
                },
                title: {
                    text: 'Storage Used',
                    
                    style:{
                        fontFamily:$('body').css('font-family'),
                        display:'none'
                    }
                },
                tooltip: {
                    formatter: function() {
                        return '<b>' + this.point.name + '</b>: ' + human_size(Math.round(this.y));
                    },    
                    style:{
                        fontFamily:$('body').css('font-family'),
                    }
                },
                legand: {
                    enabled:true
                },
                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        dataLabels: {
                            align:'left',
                            enabled: false,
                             //Highcharts.theme.textColor || '#000000',
                        //    connectorColor: Highcharts.theme.textColor || '#000000',
                            formatter: function() {
                                return this.point.name + ': ' + Math.round(this.percentage) + '%';
                            },
                            style:{
                                fontFamily:$('body').css('font-family'),
                                fontWeight:"normal",
                                fontSize:12,
                            }
                        },
                        size:'100%'
                    }
                },
                series: [{
                    type: 'pie',
                    name: 'File Sizes',
                    data: data,
                }]
            });
            
            return this
        }
    });
});