var graphs ={
	"paint_graph": function(x, data){
		d3.select(".graph_cont").html('');
		this[x].func(data);
	},
	"0": {
		"name": "Bar Graph",
		"func": function(data){
			var margin = {top: 20, right: 20, bottom: 70, left: 50},
			    width = 600 - margin.left - margin.right,
			    height = 300 - margin.top - margin.bottom;

			var x = d3.scale.ordinal().rangeRoundBands([0, width], .05);

			var y = d3.scale.linear().range([height, 0]);

			var xAxis = d3.svg.axis()
			    .scale(x)
			    .orient("bottom");

			var yAxis = d3.svg.axis()
			    .scale(y)
			    .orient("left")
			    .ticks(10)
			    .tickFormat(function (d) {
			        var prefix = d3.formatPrefix(d);
			        return prefix.scale(d) + prefix.symbol;
			    });

			var svg = d3.select(".graph_cont").append("svg")
				.attr("id","main_svg")
			    .attr("width", width + margin.left + margin.right + 20)
			    .attr("height", height + margin.top + margin.bottom + 20)
			    .append("g")
			    .attr("transform", 
			          "translate(" + (margin.left+20) + "," + (margin.top + 20) + ")");


			x.domain(data.map(function(d) { return d.label; }));
			y.domain([Math.min(0,d3.min(data, function(d) { return d.value; })) ,Math.max(0, d3.max(data, function(d) { return d.value; }))]).nice();

			svg.append("g")
				.attr("class", "x axis")
				.attr("transform", "translate(0," + (height ) + ")")
				.call(xAxis)
				.selectAll("text")
				.style("text-anchor", "end")
				.attr("dx", "-.8em")
				.attr("dy", "-.55em")
				.attr("transform", "rotate(-90)" );

			svg.append("g")
				.attr("class", "y axis")
				.call(yAxis)
				.append("text")
				.attr("transform", "rotate(-90)")
				.attr("y", 0 - margin.left)
        		.attr("x",0 - (height / 2))
				.attr("dy", ".71em")
				.style("text-anchor", "end")
				.text("Value ($)");
			
			svg.append("g")
				.attr("class","x_axis_zero axis")
		        .attr("transform", "translate(0," + y(0) + ")")
		        .call(xAxis.tickFormat("").tickSize(0));

			svg.selectAll("rect")
				.data(data)
				.enter().append("rect")
				.style("fill", "steelblue")
				.attr("x", function(d) { return x(d.label); })
				.attr("width", x.rangeBand())
				.attr("y", function(d) { return d.value < 0 ? y(0) : y(d.value); })
				.attr("height", function(d) { return Math.abs(y(d.value) - y(0)); });
		}
	},
	"trash1": {
			"name": 'Bar Graph',
			"func": function(data){
				var x = d3.scale.linear()
				    .domain([0, d3.max(data, function(d) { return d.value; })])
				    .range([0, 420]);

				items =  d3.select(".graph_cont").selectAll("div").data(data);
				items.enter().append("div");
				items.exit().remove();
				items.style("width", function(d) { return x(d.value) + "px"; })
					.text(function(d) { return d.label + ' : ' + d.value; });
			}
		 },
	"1": {
			"name": 'Pie Graph', 
			"func": function(data){
				var key = function(d){ return d.data.label; };
				var svg = d3.select(".graph_cont")
				.append("svg")
				.append("g")

				svg.append("g")
					.attr("class", "slices");
				svg.append("g")
					.attr("class", "labels");
				svg.append("g")
					.attr("class", "lines");

				var width = 960,
				    height = 450,
					radius = Math.min(width, height) / 2;

				var pie = d3.layout.pie()
					.sort(null)
					.value(function(d) {
						return d.value;
					});

				var arc = d3.svg.arc()
					.outerRadius(radius * 0.8)
					.innerRadius(radius * 0.6);

				var outerArc = d3.svg.arc()
					.innerRadius(radius * 0.7)
					.outerRadius(radius * 0.9);

				svg.attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

				d3.select('svg').style("width", width).style("height", height);

				/* ------- PIE SLICES -------*/
				var slice = svg.select(".slices").selectAll("path.slice")
					.data(pie(data), key);

				slice.enter()
					.insert("path")
					.style("fill", function(d) { return color(d.data.label); })
					.attr("class", "slice");

				slice		
					.transition().duration(1000)
					.attrTween("d", function(d) {
						this._current = this._current || d;
						var interpolate = d3.interpolate(this._current, d);
						this._current = interpolate(0);
						return function(t) {
							return arc(interpolate(t));
						};
					})

				slice.exit()
					.remove();

				/* ------- TEXT LABELS -------*/

				var text = svg.select(".labels").selectAll("text")
					.data(pie(data), key);

				text.enter()
					.append("text")
					.attr("dy", ".35em")
					.text(function(d) {
						return d.data.label;
					});
				
				function midAngle(d){
					return d.startAngle + (d.endAngle - d.startAngle)/2;
				}

				text.transition().duration(1000)
					.attrTween("transform", function(d) {
						this._current = this._current || d;
						var interpolate = d3.interpolate(this._current, d);
						this._current = interpolate(0);
						return function(t) {
							var d2 = interpolate(t);
							var pos = outerArc.centroid(d2);
							pos[0] = radius * (midAngle(d2) < Math.PI ? 1 : -1);
							return "translate("+ pos +")";
						};
					})
					.styleTween("text-anchor", function(d){
						this._current = this._current || d;
						var interpolate = d3.interpolate(this._current, d);
						this._current = interpolate(0);
						return function(t) {
							var d2 = interpolate(t);
							return midAngle(d2) < Math.PI ? "start":"end";
						};
					});

				text.exit()
					.remove();

				/* ------- SLICE TO TEXT POLYLINES -------*/

				var polyline = svg.select(".lines").selectAll("polyline")
					.data(pie(data), key);
				
				polyline.enter()
					.append("polyline");

				polyline.transition().duration(1000)
					.attrTween("points", function(d){
						this._current = this._current || d;
						var interpolate = d3.interpolate(this._current, d);
						this._current = interpolate(0);
						return function(t) {
							var d2 = interpolate(t);
							var pos = outerArc.centroid(d2);
							pos[0] = radius * 0.95 * (midAngle(d2) < Math.PI ? 1 : -1);
							return [arc.centroid(d2), outerArc.centroid(d2), pos];
						};			
					});
				
				polyline.exit()
					.remove();
			}
		 },
}
