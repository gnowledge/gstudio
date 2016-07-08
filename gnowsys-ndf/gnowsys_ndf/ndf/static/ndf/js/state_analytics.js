// Variables here==================================

var objects = [
  {"name": "Object1", "value": 0},
  {"name": "Object2", "value": 1},
  {"name": "Object3", "value": 2},
]
var dataset = [
  [
    [{"label":"Lorem ipsum","value": 83},{"label":"dolor sit","value":16},{"label":"amet","value":54},{"label":"consectetur","value":60},{"label":"adipisicing","value":68},{"label":"elit","value":46},{"label":"sed","value":35},{"label":"do","value":89},{"label":"eiusmod","value":32},{"label":"tempor","value":30},{"label":"incididunt","value":20}],
    [{"label":"Lorem ipsum","value":93},{"label":"dolor sit","value":18},{"label":"amet","value":42},{"label":"consectetur","value":28},{"label":"adipisicing","value":70},{"label":"elit","value":72},{"label":"sed","value":3},{"label":"do","value":88},{"label":"eiusmod","value":24},{"label":"tempor","value":87},{"label":"incididunt","value":32}],
  ],
  [
    [{"label":"Lorem ipsum","value":20},{"label":"dolor sit","value":26},{"label":"amet","value":62},{"label":"consectetur","value":31},{"label":"adipisicing","value":7},{"label":"elit","value":32},{"label":"sed","value":88},{"label":"do","value":81},{"label":"eiusmod","value":72},{"label":"tempor","value":52},{"label":"incididunt","value":99}],
    [{"label":"Lorem ipsum","value":44},{"label":"dolor sit","value":10},{"label":"amet","value":13},{"label":"consectetur","value":60},{"label":"adipisicing","value":44},{"label":"elit","value":56},{"label":"sed","value":67},{"label":"do","value":46},{"label":"eiusmod","value":92},{"label":"tempor","value":49},{"label":"incididunt","value":16}],
  ],
  [
    [{"label":"Lorem ipsum","value":8},{"label":"dolor sit","value":90},{"label":"amet","value":29},{"label":"consectetur","value":58},{"label":"adipisicing","value":82},{"label":"elit","value":34},{"label":"sed","value":21},{"label":"do","value":85},{"label":"eiusmod","value":37},{"label":"tempor","value":51},{"label":"incididunt","value":27}],
  ]
];

var mapping =[
  {
    "dataset": 0,
    "graph_type": [0]
  },
  {
    "dataset": 1,
    "graph_type": [0, 1]
  },
  {
    "dataset": 2,
    "graph_type": [1]
  },
];

var states_code = [
  {"code": "AP", "name": "Andhra Pradesh"},
  {"code": "AR", "name": "Arunachal Pradesh"},
  {"code": "AS", "name": "Assam"},
  {"code": "BR", "name": "Bihar"},
  {"code": "CT", "name": "Chhattisgarh"},
  {"code": "DL", "name": "Delhi"},
  {"code": "GA", "name": "Goa"},
  {"code": "GJ", "name": "Gujarat"},
  {"code": "HR", "name": "Haryana"},
  {"code": "HP", "name": "Himachal Pradesh"},
  {"code": "JK", "name": "Jammu & Kashmir"},
  {"code": "JH", "name": "Jharkhand"},
  {"code": "KA", "name": "Karnataka"},
  {"code": "KL", "name": "Kerala"},
  {"code": "MP", "name": "Madhya Pradesh"},
  {"code": "MH", "name": "Maharashtra"},
  {"code": "MN", "name": "Manipur"},
  {"code": "ML", "name": "Meghalaya"},
  {"code": "MZ", "name": "Mizoram"},
  {"code": "NL", "name": "Nagaland"},
  {"code": "OR", "name": "Odisha"},
  {"code": "PB", "name": "Punjab"},
  {"code": "RJ", "name": "Rajasthan"},
  {"code": "SK", "name": "Sikkim"},
  {"code": "TN", "name": "Tamil Nadu"},
  {"code": "TL", "name": "Telangana"},
  {"code": "TR", "name": "Tripura"},
  {"code": "UT", "name": "Uttarakhand"},
  {"code": "UP", "name": "Uttar Pradesh"},
  {"code": "WB", "name": "West Bengal"}
];


var m_width,
  width = 938,
  height = 450,
  country,
  state,
  dflt_zoom,
  projection,
  path,
  zoom_behavior,
  svg,
  city_hover_tooltip,
  g;


var pnt=true;
var organizations;
var curr_edit;
var curr = 0;
var g_cir;

var drag = d3.behavior.drag()
.on("dragstart", function(){d3.event.sourceEvent.stopPropagation();})
.on("drag", dragmove);

//variables end=======================================


//Events=============================================================
$(document).ready(function(){
  m_width = document.getElementById('map').getBoundingClientRect().width;
  dflt_zoom = [680, 250, 5];

  projection = d3.geo.mercator()
      .scale(150)
      .translate([width / 2, height / 1.5]);

  path = d3.geo.path()
      .projection(projection);
  zoom_behavior = d3.behavior.zoom();
  svg = d3.select("#map").append("svg")
      .attr("id","main_svg")
      .attr("preserveAspectRatio", "xMidYMid")
      .attr("viewBox", "0 0 " + width + " " + height)
      .attr("width", m_width)
      .attr("height", m_width * height / width)
      .call(zoom_behavior.on('zoom',redraw));


  city_hover_tooltip = d3.select("#map").append("div")
      .attr("class", "city_hover_tooltip");

  city_hover_tooltip.append("div");

  svg.append("rect")

      .attr("class", "background")
      .attr("width", width)
      .attr("height", height)
      .on("click", state_clicked);

  g = svg.append("g");

  d3.json("/static/ndf/js/india_map.topo.json", function(error, states) {
    g.append("g")
      .attr("id", "countries")
      .selectAll("path")
      .data(topojson.feature(states, states.objects.collection).features)
      .enter()
      .append("path")
      .attr("id", function(d) { return d.id; })
      .attr("d", path)
      .on("click", state_clicked)
      .on('mouseover', function(d){
        if(!$('#info_bar').hasClass('disabled')){
          $('#info_bar').text(d.properties.name);
          $('#info_bar').show();
        }
      })
      .on('mouseout', function(d){
        $('#info_bar').hide();
      })
    g_cir = g.append("g").attr("id", "circles_group");
    zoom(dflt_zoom);
    load_organization();
  });
});

window.onload = function(){
  init_lb();
}

window.onresize = function() {
  var w = document.getElementById('map').getBoundingClientRect().width;
  if(svg){
    svg.attr("width", w);
    svg.attr("height", w * height / width);
  }
};



$(document).on("click",".city",function(){
  data = {
    "head":d3.select(this).data()[0].properties.name + " Analytics",
    "content":'<div id="main_container">\
        <div class="select_wrapper">\
          <select id="object_type">\
            <option disabled selected value> -- select an option -- </option>\
            <optgroup class="opt_to_select"> </optgroup>\
          </select>\
          <select id="dataset">\
            <option selected value=""> -- select an option -- </option>\
            <optgroup class="opt_to_select"> </optgroup>\
          </select>\
          <select id="graph_type">\
            <option selected value=""> -- select an option -- </option>\
            <optgroup class="opt_to_select"> </optgroup>\
          </select>\
        </div>\
        <div class="graph_cont">\
        </div>\
      </div>',
  }
  set_content_lb(data);
  graph_select_init();

  open_lb();
});


$(document).on("mouseenter",'.city',function(e){

  var dt = d3.select(this).data()[0];
  var x = e.pageX - $('#map').offset().left;
  var y = e.pageY - $('#map').offset().top;
  city_hover_tooltip.select('div').html(dt.properties.name);
  city_hover_tooltip.style("left",x +'px')
  .style("top",y + 'px')
  .style("display","block");

});


$(document).on("mouseout",'.city',function(){
  city_hover_tooltip.select('div').html("")
  city_hover_tooltip.style("display","none");

});

$(document).on("click",".edit_city",function(){edit_org_form_init(this); });

$(document).on("click",".save_btn",function(){
  var dt = curr_edit.data()[0];
  dt.properties.name = $('#city_name').val();
  dt.properties.state = $('#state_list').val();
  curr_edit.data(dt);
  close_lb();
  update_organization(dt,dt.id);
});
$(document).on("click",".delete_btn",function(){
  var dt = curr_edit.data()[0];
  if(dt.id!==undefined)
    delete_organization(dt.id);
  else
    curr_edit.remove();
  close_lb();
});

$(document).on("click",'.edit_btn', function(){
  if(pnt){
    $('.edit_btn').text('Exit edit mode');
    g.select("#organization").remove();

    g_cir = g.append("g")
      .attr("id", "edit_mode")

    g_cir.selectAll("circle")
      .data(organizations)
      .enter()
      .append("circle")
      .attr("r", "0.5")
      .attr("class", "edit_city")
      .attr("id", function(d) { return d.properties.name; })
      .attr("transform", function(d){ return "translate(" + d.coordinates[0] + "," + d.coordinates[1] + ")"})
      .call(drag);

    $('#info_bar').addClass('disabled');

    pnt = false;
  }
  else{
    $('.edit_btn').text('Edit');
    g.select("#edit_mode").remove();
    pnt = true;
    $('#info_bar').removeClass('disabled');
    zoom(dflt_zoom);
    load_organization();
  }
});



//Events End=============================================================


//Functions=============================================================


  // Light box functions=======================================
  function init_lb(){
    var ele = '<div id="lightbox" class="fix_center"> <div id="blackout_lb" class="fix_center"></div> <div id="modal_lb"><a class="close_lb_btn" aria-label="Close">&#215;</a><h3 class="header_lb"></h3><div class="content_lb"></div></div> </div></div>';
    $('body').append(ele);
    $('#lightbox .close_lb_btn, #blackout_lb').click(function(){
      close_lb();
    })
  }
  function open_lb(){
    $('body').css('overflow', 'hidden');
    $('#lightbox').fadeIn(0);
  }
  function close_lb(){
    $('body').css('overflow', '');
    $('#lightbox').fadeOut(0);
  }

  function set_content_lb(data){
    if(data === undefined){
      data = {};
    }
    if(data.head === undefined){
      data.head = "";
    }
    if(data.content === undefined){
      data.content = "";
    }
    $('#modal_lb .header_lb').html(data.head);
    $('#modal_lb .content_lb').html(data.content);
  }
  // Light box functions================END=======================


function graph_select_init(){
  load_obj();
  d3.select('#object_type').on('change', function(){
    var val = mapping[this.value];

    d3.select('#dataset').select('.opt_to_select')
      .html('');
    var ele = d3.select('#dataset').select('.opt_to_select');
    for(i=0 ; i< dataset[val.dataset].length; i++){
      ele.append('option')
        .attr('value',i)
        .html('Dataset '+ i);
    }

    d3.select('#graph_type').select('.opt_to_select')
      .html('');
    var ele = d3.select('#graph_type').select('.opt_to_select');
    for(i=0; i<val.graph_type.length; i++){
      ele.append('option')
        .attr('value', i)
        .html(graphs[i].name);
    }

    d3.select(".graph_cont").html('');

  });

  d3.selectAll('#dataset, #graph_type').on('change', function(){
    refresh_graphs();
  });
}

function load_obj(){
  d3.select('#object_type').select('.opt_to_select')
    .html('');
  var ele = d3.select('#object_type').select('.opt_to_select');
  for(i=0 ;i<objects.length; i++){
    ele.append('option')
      .attr('value',objects[i].value)
      .html(objects[i].name);
  }
}

function refresh_graphs(){
  var object_type, ds, graph_type;
  object_type = d3.select('#object_type').node().value;
  ds = d3.select('#dataset').node().value;
  graph_type = d3.select('#graph_type').node().value;
  if(ds != '' && graph_type != '')
    graphs.paint_graph(graph_type, dataset[mapping[object_type].dataset][ds]);

}

function redraw(){
  if(pnt){
    return;
  }
  var s = d3.event.scale;
  var t = d3.event.translate;
  g.style("stroke-width",1/s).attr("transform","translate("+t+")scale("+s+")");
}

function edit_org_form_init(obj){
  curr_edit = d3.select(obj);
  data = {
    "head":"Edit City",
    "content":'Name: <input id="city_name" type="text" /> \
            State: \
            <select id="state_list"></select><br>\
            <a class="save_btn button">Save</a><a class="delete_btn button">Delete</a>',
  }
  set_content_lb(data);
  var $st_list = $('#state_list');
  for(i=0; i<states_code.length; i++){
    $st_list.append('<option value="'+states_code[i].code+'">'+states_code[i].name+'</option>')
  }
  var dt = curr_edit.data()[0];
  $('#city_name').val(dt.properties.name);
  $('#state_list').val(dt.properties.state);
  open_lb();
}
function zoom(xyz) {
  g.transition()
    .duration(750)
    .attr("transform", "translate(" + projection.translate() + ")scale(" + xyz[2] + ")translate(-" + xyz[0] + ",-" + xyz[1] + ")")
    .selectAll(["#countries", "#states", "#organization"])
    .style("stroke-width", 1.0 / xyz[2] + "px")
    .selectAll(".city")
    .attr("d", path.pointRadius(20.0 / xyz[2]));

  var t = projection.translate();
  t[0] = (xyz[0]*xyz[2] - t[0])*-1;
  t[1] = (xyz[1]*xyz[2] - t[1])*-1;
  zoom_behavior.scale(xyz[2]).translate(t)
  return;
}

function get_xyz(d) {
  var bounds = path.bounds(d);
  var w_scale = (bounds[1][0] - bounds[0][0]) / width;
  var h_scale = (bounds[1][1] - bounds[0][1]) / height;
  var z = .96 / Math.max(w_scale, h_scale);
  var x = (bounds[1][0] + bounds[0][0]) / 2;
  var y = (bounds[1][1] + bounds[0][1]) / 2 + (height / z / 6);
  return [x, y, z];
}

function state_clicked(d){
	if(pnt){
		state_clicked2(d);
		return;
	}
	if (d3.event.defaultPrevented) return;

	var point = d3.mouse(this)
	, p = {x: point[0], y: point[1] };

	// Append a new point
  var dt = [{
    properties:{
      name: "",
      state: "",
    },
    coordinates:[(p.x), (p.y)],
  }];

	var new_cir = g_cir.append("circle");
	new_cir.data(dt);

	new_cir.attr("transform", "translate(" + p.x + "," + p.y + ")")
		.attr("r", "0.5")
		.attr("class", "edit_city")
		.style("cursor", "pointer")
		.call(drag);

  edit_org_form_init($(new_cir)[0][0]);
}

function dragmove(d) { 
  var x = d3.event.x;
  var y = d3.event.y;

  var dt = d3.select(this).data()[0];
  dt.coordinates[0] = x;
  dt.coordinates[1] = y;
  d3.select(this).data(dt);
  d3.select(this).attr("transform", "translate(" + x + "," + y + ")");
}

function state_clicked2(d) {
  g.selectAll("#organization").remove();

  if (d && state !== d) {
    var xyz = get_xyz(d);
    state = d;
    state_name = d.id;

      g.append("g")
        .attr("id", "organization")
        .selectAll("circle")
        .data(organizations.filter(function(d) { return state_name == d.properties.state; }))
        .enter()
        .append("circle")
        .attr("r", "0.5")
        .attr("class", "city")
        .attr("id", function(d) { return d.properties.name; })
        .attr("transform", function(d){ return "translate(" + d.coordinates[0] + "," + d.coordinates[1] + ")"})

      zoom(xyz);
      $('#info_bar').addClass('disabled');

  } else {
    state = null;
    zoom(dflt_zoom);
    $('#info_bar').removeClass('disabled');
  }
}

function load_organization(){
  $.ajax({
    url: '/{{groupid}}/state_analytics/fetch_organization',
    method: 'GET',
    success: function(data){
      var det = JSON.parse(data);
      for(i=0; i<det.length; i++){
       det[i] = JSON.parse(det[i]);
      }
      organizations = det;
    }
  });
}

function update_organization(data,id){
  if(id===undefined)
  {
    id = '';
  }
  $.ajax({
    url: '/{{groupid}}/state_analytics/update_organization/' + id,
    method: 'POST',
    data: JSON.stringify(data),
    success: function(data){
      data = JSON.parse(data);
      curr_edit.data()[0]['id'] = data.id;
      curr_edit.attr('id', data.id);
    }
  });
}

function delete_organization(id){
  if(id===undefined){
    return;
  }
  $.ajax({
    url: '/{{groupid}}/state_analytics/delete_organization/' + id,
    method: 'POST',
    success: function(data){
      data = JSON.parse(data);
      if(data.status)
        curr_edit.remove();
    }
  });
}
//Function end===============================================================