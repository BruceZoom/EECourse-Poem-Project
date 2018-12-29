function plot_force_direct_graph(source, svg_id="#cn"){
	var colors = new Array("#912CEE", "#66ccff", "#8B008B", "#CD853F");

	var svg = d3.select(svg_id),
		width = +svg.attr("width"),
		height = +svg.attr("height");
		

	var simulation = d3.forceSimulation()
		.force("link", d3.forceLink().id(function(d) { return d.id; }))
		.force("charge", d3.forceManyBody())
		.force("center", d3.forceCenter(width / 2, height / 2));
		
	d3.json(source, function(error, graph) {
	  if (error) throw error;

	  var link = svg.append("g")
		  .attr("class", "links")
		.selectAll("line")
		.data(graph.links)
		.enter().append("line")
		  .attr("stroke-width", function(d) { return Math.sqrt(d.value); });

	  var node = svg.append("g")
		  .attr("class", "nodes")
		.selectAll("circle")
		.data(graph.nodes)
		.enter().append("circle")
		  .attr("r", 5)
		  .attr("fill", function(d) { return colors[d.group-1]; })
		  .call(d3.drag()
			  .on("start", dragstarted)
			  .on("drag", dragged)
			  .on("end", dragended));

	  node.append("title")
		  .text(function(d) { return d.id; });

	  simulation
		  .nodes(graph.nodes)
		  .on("tick", ticked);

	  simulation.force("link")
		  .links(graph.links);

	  function ticked() {
		link
			.attr("x1", function(d) { return d.source.x; })
			.attr("y1", function(d) { return d.source.y; })
			.attr("x2", function(d) { return d.target.x; })
			.attr("y2", function(d) { return d.target.y; });

		node
			.attr("cx", function(d) { return d.x; })
			.attr("cy", function(d) { return d.y; });
	  }
	});

	function dragstarted(d) {
	  if (!d3.event.active) simulation.alphaTarget(0.3).restart();
	  d.fx = d.x;
	  d.fy = d.y;
	}

	function dragged(d) {
	  d.fx = d3.event.x;
	  d.fy = d3.event.y;
	}

	function dragended(d) {
	  if (!d3.event.active) simulation.alphaTarget(0);
	  d.fx = null;
	  d.fy = null;
	}
}

function plot_publication_increament(source, mode=1, svg_id="#pi"){
	var svg = d3.select(svg_id + mode),
		margin = {
			top: 20,
			right: 20,
			bottom: 30,
			left: 50
		},
		width = +svg.attr("width") - margin.left - margin.right,
		height = +svg.attr("height") - margin.top - margin.bottom,
		g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
		
	var x = d3.scaleLinear()
		.rangeRound([0, width]);
		
	var y = d3.scaleLinear()
		.rangeRound([height, 0]);

	var line = d3.line()
		.x(function(d) { return x(d.year); })
		.y(function(d) { return y(d.publication); });
		
	var area = d3.area()
		.x(function(d) { return x(d.year); })
		.y1(function(d) { return y(d.publication); });
	
	function plot_area(data, ylabel){
			x.domain([d3.min(data, function(d){ return +d.year - 1; }), d3.max(data, function(d){ return +d.year + 1; })]);
			y.domain([0, d3.max(data, function(d){ return +d.publication + 1; })]);
			area.y0(y(0));
			
			g.append("path")
				.datum(data)
				.attr("fill", "steelblue")
				.attr("d", area);
			
			g.append("g")
				.attr("transform", "translate(0," + height + ")")
				.call(d3.axisBottom(x))
				.attr("class", "axis")
			 .append("text")
				.attr("fill", "#000")
				.attr("x", 850)
				.attr("dy", "-0.5em")
				.attr("text-anchor", "start")
				.text("Year")
			
			g.append("g")
				.call(d3.axisLeft(y))
				.attr("class", "axis")
			 .append("text")
				.attr("fill", "#000")
				.attr("transform", "rotate(-90)")
				.attr("y", 6)
				.attr("dy", "0.71em")
				.attr("text-anchor", "end")
				.text(ylabel);
	}
	
	if(mode==1){
		d3.json(source, function(error, data){
			if(error) throw error;
			
			plot_area(data, "Annual Publication");
		});
	}
	else if(mode==2){
		d3.json(source, function(error, data){
			if(error) throw error;
			
			plot_area(data, "Total Publication")
		});
	}
}

// abandoned
function plot_box_chart(source, svg_id="#rbp"){
	var chart1;
    d3.json(source, function(error, data) {
        data.forEach(function (d) {d.reference = +d.reference;});

        chart1 = makeDistroChart({
            data:data,
            xName:'year',
            yName:'value',
            axisLabels: {xAxis: 'Year', yAxis: 'Cited Times'},
            selector:svg_id,
            chartSize:{height:500, width:750},
            constrainExtremes:true});
        chart1.renderBoxPlot();
        chart1.renderDataPlots();
        chart1.renderNotchBoxes({showNotchBox:false});
        chart1.renderViolinPlot({showViolinPlot:true});

    });
	/*var svg = d3.select(svg_id),
		margin = {top: 10, right: 50, bottom: 20, left: 50},
		width = +svg.attr("width") - margin.left - margin.right,
		height = +svg.attr("height") - margin.top - margin.bottom;

	var min = Infinity,
	max = -Infinity;

	var chart = d3.box()
		.whiskers(iqr(1.5))
		.width(width)
		.height(height);

	d3.json(source, function(error, ori_data) {
	if (error) throw error;

	var data = [];

	for(var i=0;i<ori_data.length;i++){
		s = ori_data[i].reference;
		d = data[ori_data[i].year] = s;
		for(var j=0;j<s.length;j++){
			if (s[j] > max) max = s[j];
			if (s[j] < min) min = s[j];
		}
	}

	chart.domain([min, max]);

	svg.data(data)
	  .attr("class", "box")
	  .attr("width", width + margin.left + margin.right)
	  .attr("height", height + margin.bottom + margin.top)
	.append("g")
	  .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
	  .call(chart);

	setInterval(function() {
	svg.datum(randomize).call(chart.duration(1000));
	}, 2000);
	});

	function randomize(d) {
	if (!d.randomizer) d.randomizer = randomizer(d);
	return d.map(d.randomizer);
	}

	function randomizer(d) {
	var k = d3.max(d) * .02;
	return function(d) {
	return Math.max(min, Math.min(max, d + k * (Math.random() - .5)));
	};
	}

	// Returns a function to compute the interquartile range.
	function iqr(k) {
		return function(d, i) {
			var q1 = d.quartiles[0],
				q3 = d.quartiles[2],
				iqr = (q3 - q1) * k,
				i = -1,
				j = d.length;
			while (d[++i] < q1 - iqr);
			while (d[--j] > q3 + iqr);
			return [i, j];
		};
	}*/
	
};
	
function plot_vertical_bar(source, svg_id, mode){
	var svg = d3.select(svg_id),
    margin = {top: 20, right: 20, bottom: 50, left: 40},
    width = +svg.attr("width") - margin.left - margin.right,
    height = +svg.attr("height") - margin.top - margin.bottom;

	var x = d3.scaleBand().rangeRound([0, width]).padding(0.1),
		y = d3.scaleLinear().rangeRound([height, 0]);

	var g = svg.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	d3.json(source, function(error, data) {
	  if (error) throw error;

	function xv(d){
		if(mode=="ref") return d.year;
		else if(mode=="top") return d.name;
	}
	function yv(d){
		if(mode=="ref") return d.number;
		else if(mode=="top") return d.papers;
	}
	  
	  x.domain(data.map(function(d) { return xv(d); }));
	  y.domain([0, d3.max(data, function(d) { return yv(d); })]);

	  g.append("g")
		  .attr("class", "axis axis--x")
		  .attr("transform", "translate(0," + height + ")")
		  .call(d3.axisBottom(x))
		.selectAll("text")
		  .attr("dx", "-3em")
		  .attr("transform", "rotate(-30)");

	  g.append("g")
		  .attr("class", "axis axis--y")
		  .call(d3.axisLeft(y))
		.append("text")
		  .attr("transform", "rotate(-90)")
		  .attr("y", 6)
		  .attr("dy", "0.71em")
		  .attr("text-anchor", "end")
		  .text("Numer of Papers");

	  g.selectAll(".bar")
		.data(data)
		.enter().append("rect")
		  .attr("class", "bar")
		  .attr("x", function(d) { return x(xv(d)); })
		  .attr("y", function(d) { return y(yv(d)); })
		  .attr("width", x.bandwidth())
		  .attr("height", function(d) { return height - y(yv(d)); });
	});
}

function plot_dynamic_force_direct_graph(source, svg_id, updateSourcePrefix=null){
	var colors = new Array("#66ccff", "#C15CFE");
	var ar_color = "#8B008B",
		ae_color = "#CD853F",
		hl_color = "#912CEE";
	
	
	var svg = d3.select(svg_id),
		width = +svg.attr("width"),
		height = +svg.attr("height");
		
	var simulation = d3.forceSimulation()
		.force("link", d3.forceLink().id(function(d) { return d.id; }))
		.force("charge", d3.forceManyBody())
		.force("center", d3.forceCenter(width / 2, height / 2));
	
	var nodes_memo = new Array(),
		links_memo = new Array();
	
	function updateChart(sourceFile){	
		d3.json(sourceFile, function(error, data) {
		  if (error) throw error;
		  
		  data.nodes.forEach(function(d){
			  var i = nodes_memo.findIndex(function(x){
				  return x.id == d.id;
			  });
			  if(i < 0){
				  nodes_memo.push(d);
			  }
			  /*else{
				  nodes_memo[i].group = max(nodes_memo[i].group, d.group);
				  d.advisors.forEach(function(ad){
					  if(nodes_memo[i].advisors.indexOf(ad) >= 0)
						  nodes_memo[i].advisors.push(ad);
			      });
				  d.advisees.forEach(function(ad){
					  if(nodes_memo[i].advisees.indexOf(ad) >= 0)
						  nodes_memo[i].advisees.push(ad);
			      });
			  }*/
		  });
		  data.links.forEach(function(d){
			  if(links_memo.findIndex(function(x){
				  return (x.source == d.source && x.target == d.target)
					|| (x.source == d.target && x.target == d.source);
			  }) < 0)
				  links_memo.push(d);
		  });
		  
		  svg.selectAll("line").remove();
		  var link = svg.append("g")
			  .attr("class", "links")
			.selectAll("line")
			.data(links_memo)
			.enter().append("line")
			  .attr("stroke-width", function(d) { return Math.sqrt(d.value); });

		  svg.selectAll("circle").remove();
		  var node = svg.append("g")
			  .attr("class", "nodes")
			.selectAll("circle")
			.data(nodes_memo)
			.enter().append("circle")
			  .attr("r", 5)
			  .attr("class", function(d){ return "node-id-"+d.id; })
			  .attr("fill", function(d) { return colors[d.group-1]; })
			  .call(d3.drag()
				  .on("start", node_dragstarted)
				  .on("drag", node_dragged)
				  .on("end", node_dragended));

		  node.append("title")
			  .text(function(d) { return d.id; });

		  simulation
			  .nodes(nodes_memo)
			  .on("tick", ticked);
		
		if(updateSourcePrefix!=null)
			d3.selectAll("circle")
				.on("click", node_on_click);

		  simulation.force("link")
			  .links(links_memo);

		  function ticked() {
			link
				.attr("x1", function(d) { return d.source.x; })
				.attr("y1", function(d) { return d.source.y; })
				.attr("x2", function(d) { return d.target.x; })
				.attr("y2", function(d) { return d.target.y; });

			node
				.attr("cx", function(d) { return d.x; })
				.attr("cy", function(d) { return d.y; });
		  }
		});
	}
	
	updateChart(source);
	
	function node_dragstarted(d) {
	  if (!d3.event.active) simulation.alphaTarget(0.3).restart();
	  d.fx = d.x;
	  d.fy = d.y;
	  d3.select(".node-id-"+d.id)
			.attr("fill", hl_color)
	  d.advisors.forEach(function(item){
		  d3.select(".node-id-"+item)
			.attr("fill", ar_color);
	  });
	  d.advisees.forEach(function(item){
		  d3.select(".node-id-"+item)
			.attr("fill", ae_color);
	  });
	}

	function node_dragged(d) {
	  d.fx = d3.event.x;
	  d.fy = d3.event.y;
	}

	function node_dragended(d) {
	  if (!d3.event.active) simulation.alphaTarget(0);
	  d.fx = null;
	  d.fy = null;
	  d3.select(".node-id-"+d.id)
			.attr("fill", function(k){ return colors[k.group-1]; })
	  d.advisors.forEach(function(item){
		  d3.select(".node-id-"+item)
			.attr("fill", function(k){ return colors[k.group-1]; });
	  });
	  d.advisees.forEach(function(item){
		  d3.select(".node-id-"+item)
			.attr("fill", function(k){ return colors[k.group-1]; });
	  });
	}
	
	function node_on_click(d){
		updateChart(updateSourcePrefix + d.id);
	}
	
	function max(a, b){
		if(a > b) return a;
		else return b;
	}
}

function plot_conference_dist_pi_chart(source, svg_id){
	var svg = d3.select(svg_id),
		margin = {top: 20, right: 20, bottom: 20, left: 20},
		width = +svg.attr("width") - margin.left - margin.right,
		height = +svg.attr("height") - margin.top - margin.bottom,
		radius = Math.min(width, height) / 2;
	
	var arc = d3.arc()
		.outerRadius(radius - 10)
		.innerRadius(radius - 90);

	var pie = d3.pie()
		.sort(null)
		.value(function(d) { return d.number; });

	d3.json(source, function(error, data) {
	  if (error) throw error;

	  var colors = d3.scaleOrdinal()  
            .domain(data.map(function(d){
				return d.conference_id;
			}))  
            .range(d3.schemeCategory20);
	  
	  var g = svg.selectAll(".arc")
		  .data(pie(data))
		.enter().append("g")
		  .attr("class", "arc")
		  .attr("transform", "translate(" + width/2 + "," + height/2 + ")");

	  g.append("path")
		  .attr("d", arc)
		  .style("fill", function(d) { return colors(d.data.conference_id); });

	  g.append("rect")
		.attr("transform", function(d){
			i = colors.domain().indexOf(d.data.conference_id)
			var legendX = width/2 - 50;  
			var legendY = -height/2 + margin.top + i * 20 - 5;
			return "translate(" + legendX + ", " + legendY + ")";  
		})
		.attr("width", 16)
		.attr("height", 8)
		.attr("fill", function(d) { return colors(d.data.conference_id); });
		g.append("text")
		  .attr("transform", function(d) {
				i = colors.domain().indexOf(d.data.conference_id)
                var legendX = width/2; 
                var legendY = -height/2 + margin.top + i * 20;
                return "translate(" + legendX + ", " + legendY + ")";  
            })
		  .attr("dy", ".35em")
		  .attr("fill", "#fff")
		  .text(function(d) { return d.data.conference_id; });
		  
	});
}

function plot_label_cloud(source, svg_id){
	var svg = d3.select(svg_id),
		width = +svg.attr("width"),
		height = +svg.attr("height"),
		size = 40,
		maxsize = 0;
	
	d3.json(source, function(error, data) {
		if (error) throw error;

		data.forEach(function(d){
			if(maxsize < d.size)
				maxsize = d.size;
		});
		for(var i=0;i<data.length;i++)
			data[i].size = data[i].size * size / maxsize;

		var fill = d3.scaleOrdinal()
			.domain(data.map(function(d){
				return d.text;
			}))  
			.range(d3.schemeCategory20);

		d3.layout.cloud().size([width, height])
			.words(data)
			.rotate(function() { return ~~(Math.random() * 2) * 90; })
			.font("Impact")
			.fontSize(function(d) { return d.size; })
			.on("end", draw)
			.start();

		function draw(words) {
			svg.append("g")
				.attr("transform", "translate(" + width/2 + "," + height/2 + ")")
				.selectAll("text")
				.data(words)
				.enter().append("text")
				.style("border","1px solid blue")
				.style("font-size", function(d) { return d.size + "px"; })
				.style("font-family", "Impact")
				.style("fill", function(d, i) { return fill(i); })
				.attr("text-anchor", "middle")
				.attr("transform", function(d) {
					return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
				})
				.text(function(d) { return d.text; });
		}
	});
}
