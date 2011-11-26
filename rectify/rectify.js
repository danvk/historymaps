var talkToServer = false;
var endpoint = '/update_rectification';

// Given existing (x, y) -> (lat, lon) pairs, guess the (lat, lon) for (x, y)
function guessLatLon(map, pairs, x, y) {
  if (pairs.length == 0) {
    // guess the center -- we don't have anything else to go on.
    // (or, maybe do something like the next case w/ the centers as points of
    // commonality)
    var ll = map.getCenter();
    return [ ll.lat(), ll.lng() ];
  }

  if (pairs.length == 1 || pairs.length == 2) {
    // assume that the maps are just scaled versions of one another.
    var p = pairs[0];
    var x_delta = x - p.image_x;
    var y_delta = y - p.image_y;
    var map_span = map.getBounds().toSpan();
    return [p.lat - (y_delta) * map_span.lat() / $('#img').height(),
            p.lon + (x_delta) * map_span.lng() / $('#img').width()];
  }

  // With three or more points, we can do a full linear regression.
  var lats = [], lons = [], xys = [], x;
  for (var i = 0; i < pairs.length; i++) {
    lats.push(pairs[i].lat);
    lons.push(pairs[i].lon);
    xys.push([1, pairs[i].image_x, pairs[i].image_y]);
  }
  x = $V([1, x, y]);

  lat_vec = $V(lats);
  lon_vec = $V(lons);
  X = $M(xys);
  var Xt = X.transpose();
  var inv = (Xt.x(X)).inverse().x(Xt);
  var lat_params = inv.x(lat_vec);
  var lon_params = inv.x(lon_vec);

  return [ lat_params.dot(x), lon_params.dot(x) ];
}

function initialize(init_pairs) {
  var latlng = new google.maps.LatLng(25, 30);
  var opts = {
    zoom: 4,
    center: latlng,
    mapTypeId: google.maps.MapTypeId.TERRAIN,
    styles: [
      {
        featureType: "administrative",
        stylers: [
          { visibility: "off" }
        ]
      },{
        featureType: "road",
        stylers: [
          { visibility: "off" }
        ]
      },{
        featureType: "landscape.man_made",
        stylers: [
          { visibility: "off" }
        ]
      },{
        featureType: "poi",
        stylers: [
          { visibility: "off" }
        ]
      }
    ]
  };
  
  map = new google.maps.Map(document.getElementById("gmap"), opts);

  selected_marker_img = new google.maps.MarkerImage(
    'crosshair.gif',
    new google.maps.Size(32, 32),  // size
    new google.maps.Point(0, 0),   // origin
    new google.maps.Point(16, 16)  // anchor
  );
  nonselected_marker_img = new google.maps.MarkerImage(
    'dot.png',
    new google.maps.Size(32, 32),  // size
    new google.maps.Point(0, 0),   // origin
    new google.maps.Point(16, 16)  // anchor
  );

  pairs = [];

  $('#img').on('dblclick', function(evt) {
    // create a new marker pair
    var x = evt.offsetX - this.offsetLeft;
    var y = evt.offsetY - this.offsetTop;
    var guess_ll = guessLatLon(map, pairs, x, y);
    addPair(x, y, guess_ll[0], guess_ll[1]);
    updateServer();
  });

  $('#img').on('click', function() {
    $('.image_marker').removeClass('selected_marker');
  });
}

function setSelection(idx) {
  $('.image_marker').removeClass('selected_marker');
  $(pairs[idx].image_marker).addClass('selected_marker');
  for (var i = 0; i < pairs.length; i++) {
    if (i == idx) continue;
    pairs[i].map_marker.setIcon(nonselected_marker_img);
  }
  pairs[idx].map_marker.setIcon(selected_marker_img);
}

function addPair(image_x, image_y, lat, lon) {
  var pair = {
    image_x: image_x,
    image_y: image_y,
    lat: lat,
    lon: lon,
    image_marker: null,
    map_marker: null
  };
  pairs.push(pair);

  var image_marker = $('<div></div>')
      .data('pair_num', pairs.length - 1)
      .css({
        left: image_x + 'px',
        top: image_y + 'px'
      })
      .addClass('image_marker').addClass('selected_marker')
      .on('click', function(evt) {
        setSelection($(this).data('pair_num'));
      })
      .on('mousedown', function(evt) {
        setSelection($(this).data('pair_num'));
        var state = {
          dragStartPageX: evt.pageX,
          dragStartPageY: evt.pageY,
          startLeft: parseInt($(this).css('left')),
          startTop: parseInt($(this).css('top')),
          marker: this
        };
        $('#left').on('mousemove', '', state, function(evt) {
          var movement_x = evt.pageX - evt.data.dragStartPageX;
          var movement_y = evt.pageY - evt.data.dragStartPageY;
          $(evt.data.marker).css({
            left: evt.data.startLeft + movement_x + 'px',
            top: evt.data.startTop + movement_y + 'px'
          });
        }).on('mouseup', '', state, function(evt) {
          var final_x = evt.data.startLeft + evt.pageX - evt.data.dragStartPageX;
          var final_y = evt.data.startTop + evt.pageY - evt.data.dragStartPageY;
          $(evt.data.marker).css({
            left: final_x + 'px',
            top: final_y + 'px'
          });
          var pair = pairs[$(evt.data.marker).data('pair_num')];
          pair.image_x = final_x;
          pair.image_y = final_y;
          $(this).off('mousemove');
          $(this).off('mouseup');
          updateServer();
        });
      })
      ;
  $('#left').append(image_marker);
  pair.image_marker = image_marker;

  var marker = new google.maps.Marker({
    position: new google.maps.LatLng(pair.lat, pair.lon),
    map: map,
    visible: true,
    icon: selected_marker_img,
    draggable: true,
    raiseOnDrag: false,
  });
  google.maps.event.addListener(marker, 'dragend', (function(i) {
    return function(evt) {
      pairs[i].lat = evt.latLng.lat();
      pairs[i].lon = evt.latLng.lng();
      updateServer();
    }
  })(pairs.length - 1));

  pair.map_marker = marker;
  setSelection(pairs.length - 1);
}

function updateServer() {
  var data = {
    image: $('#img').attr('src'),
    pairs: [
    ]
  };

  for (var i = 0; i < pairs.length; i++) {
    var p = pairs[i];
    data.pairs.push({
      lat: p.lat,
      lon: p.lon,
      image_x: p.image_x,
      image_y: p.image_y
    });
  }

  if (!talkToServer) {
    console.log(data);
  } else {
    var req = new XMLHttpRequest();
    var caller = this;
    req.open("POST", url, true);
    req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    req.send(JSON.stringify(data));
  }
}
