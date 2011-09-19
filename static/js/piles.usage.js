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
    

    
    
    //
    // Models
    //
    
    var UsageEvent = PilesIO.UsageEvent = Backbone.Model.extend({})
    var UsageEventCollection = PilesIO.UsageEventCollection = Backbone.Collection.extend({
        model:UsageEvent,
		comparator:function(uevent) {
		    return -uevent.get('date')
		}
    })

    
    //
    // Views
    //
    var UsageEventView = PilesIO.UsageEventView = Backbone.View.extend({
        
        tagName: 'tr',
        className:'usage-event',
        
        initialize:function() {
            this.$el = $(this.el)
        },
        render:function() {
            this.$el.html(_.template($("#usage-event-tpl").html(),this.model.toJSON()))
            return this
        },
    })
    
    
    
    
    var UsageView = PilesIO.UsageView = Backbone.View.extend({
        
        className: 'usage',
        
        initialize: function() {
            
        },
        
        _chart_files:function(files) {
            var total = _.reduce(files,function(memo,file) { return memo + file.get('size')}, 0)
                series = [],
                percent10 = total/10,
                cursorSize = total,
                cursor = 0;
            while (files[cursor] != undefined && cursorSize > percent10 && cursor < 8) {
                file = files[cursor]
                series.push([file.get('name'),file.get('size')])
                cursor += 1
                cursorSize -= file.get('size')
            }
            series.push(['Others...',cursorSize])
            return series;
        },
        
        _construct_usage_chart: function(custom) {
            
            var data = _.map(custom.sequence,function(m) {
                return [m.date.getTime(), m.size]
                //return [m.get('date').getTime(), m.get('size')]
            })
            
            var chart = new Highcharts.Chart({
                chart: {
                    renderTo: $(custom.elem).get(0),
                    type: 'spline',
                    backgroundColor: 'transparent',
                    plotBorderWidth: null,
                    plotShadow: false,
                    style:{
                     fontFamily:$('body').css('font-family'),
                    },
                    width:custom.width || 600,
                    height:custom.height || 160,
                },
                plotOptions: {
                    area: {
                        fillColor: {
                            linearGradient: [0, 0, 0, (custom.height || 200)/1.5],
                            stops: [
                                [0, Highcharts.getOptions().colors[0]],
                                [1, 'rgba(2,0,0,0)']
                            ]
                        }
                    },
                    line: {
                       dataLabels: {
                          enabled: true
                       },
                       enableMouseTracking: false
                    }
                },
                title: {
                    text: null,
                },
                xAxis: {
                    type: 'datetime',
                },
                legend: {
                    enabled:false
                },
                yAxis: {
                    title: {
                        text:null
                    }
                },
                tooltip: {
                    formatter: function() {
                           return '<b>'+ this.series.name +'</b><br/>'+
                       Highcharts.dateFormat('%b %e', this.x) +': '+ PilesIO.human_size(this.y);
                }
                },
                series:[{
                    type: 'area',
                    name: custom.title,
                    data:data
                }]
          })
        
        },
        _construct_storage_pie: function() {
            var $usage_sto_pie = this.$el.find('#sto-pie')
            var data = this._chart_files(this.model.files.models)
            
            var chart = new Highcharts.Chart({
                chart: {
                    renderTo: $usage_sto_pie.get(0),
                    backgroundColor: 'transparent',
                    plotBorderWidth: null,
                    plotShadow: false,
                    style:{
                        fontFamily:$('body').css('font-family'),
                    },
                    width:600,
                    height:160,
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
                        return human_size(Math.round(this.y));
                    },    
                    style:{
                        fontFamily:$('body').css('font-family'),
                    },
                    enabled:true,
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
                        size:'100%',
                        showInLegend:true,
                    }
                },
                legend: {
                    layout:'vertical',
                    style:{
                        overflow:'hidden',
                    },
                    align:'right',
                    verticalAlign:'top',
                },
                series: [{
                    type: 'pie',
                    name: 'File Sizes',
                    data: data,
                }]
            });
        },
        
        render:function() {
            var $el = $(this.el),
                tpl = _.template($('#usage-tpl').html()),
                self = this;
            this.$el = $el
            $el.html(tpl(this.model.toJSON()))
            
            
            /* Render the most recent event lists
            var $ges = $el.find('#get-events')
            var $pes = $el.find('#put-events')
            _.each(this.model.usage_gets.models, function(m) {
                $ges.append((new UsageEventView({model:m})).render().el)
            })
            _.each(this.model.usage_puts.models, function(m) {
                $pes.append((new UsageEventView({model:m})).render().el)
            })*/

            
            // Render the PUT chart
            this._construct_usage_chart({
                title: 'Uploads',
                height:280,
                sequence: _.map(this.model.daily_puts.models,function(m) { 
                    return {date:m.get('date'),size:m.get('size') }}),
                elem:this.$el.find('#put-chart'),
            });
            // Render the GET chart
            this._construct_usage_chart({
                title: 'Downloads',
                height:280,
                sequence: _.map(this.model.daily_gets.models,function(m) { 
                    return {date:m.get('date'),size:m.get('size') }}),
                elem:this.$el.find('#get-chart'),
            });
            
            var sum = 0
            var seq = _.map(this.model.daily_sto.models,function(m) {
                sum += m.get('size')
                return {'date':m.get('date'), 'size':sum}
            })
            
            // Render the STO chart
            this._construct_usage_chart({
                title: null,
                sequence: seq,
                elem:this.$el.find('#sto-chart'),
            });
            // Render The STO pie chart
            this._construct_storage_pie();
            
            // Bind hover events 
            this.$el.find('#simple-usage-get').hover(function(e) {
                self.$el.find('.details').not('#detailed-usage-get').hide()
                self.$el.find('#detailed-usage-get').slideDown()
            })
            this.$el.find('#simple-usage-put').hover(function(e) {
                self.$el.find('.details').not('#detailed-usage-put').hide()
                self.$el.find('#detailed-usage-put').slideDown()
            })
            this.$el.find('#simple-storage').hover(function(e) {
                self.$el.find('.details').not('#detailed-storage').hide()
                self.$el.find('#detailed-storage').slideDown()
            })
            
            this.$el.find('#simple-sum').hover(function(e) {
                self.$el.find('.details').not('#detailed-sum').hide()
                self.$el.find('#detailed-sum').slideDown()
            })
            
            this.$el.find('#detailed-sum #free-progress').progressbar({ 
                value : (this.model.get('this_month_dollars') / this.model.get('freeloaders_this_month_dollars') *100) 
            })
            
            return this
        }
    });
});