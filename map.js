var min = -400;
var max = end_year;
var kExpandedBackgroundSize = 32768;
var kOriginalBackgroundWidth = 25201;
var kOriginalBackgroundHeight = 15120;

// startX/Y are in the fully-zoomed SVG coordinate system.
var startX = 12100;
var startY = 3550;
var startZoom = 5;
var maxZoom = 7;

function nameToId(name) {
  return name.replace(/ /g, '_');
}

function countryMouseOver(e) {
  $('#highlighted-country').html(e.target.getAttribute('readableName'));
  e.target.setAttribute('stroke-width', 20);
}
function countryMouseOut(e) {
  $('#highlighted-country').html('');
  e.target.setAttribute('stroke-width', 5);
}

var last_drawn_idx = -1;
function slideToYear(year) {
  var this_year_idx = 0;
  for (var i = 0; i < rome.length; i++) {
    if (rome[i][0] > year) {
      this_year_idx = i - 1;
      break;
    }
  }

  var cum_delta = {};
  var sgn = this_year_idx - last_drawn_idx < 0 ? -1 : +1;
  for (var i = last_drawn_idx + sgn; ; i += sgn) {
    var data = rome[i][1];
    for (var k in data) {
      cum_delta[k] = data[k];
    }
    if (i == this_year_idx) break;
  }
  last_drawn_idx = this_year_idx;

  for (var k in cum_delta) {
    var d = cum_delta[k];
    if (d == '') d = 'M 11445 4535 z';
    $('#' + nameToId(k)).attr("d", d);
  }

  var str = year > 0 ? 'A.D.' : 'B.C.';
  var pct = 100.0 * (year - min) / (max - min);
  $('#year')
      .text('' + Math.abs(year) + ' ' + str)
      .css('left', pct + '%');
}

$(function(){
  // create paths for all empires/nations
  for (var k in colors) {
    var el = document.createElementNS("http://www.w3.org/2000/svg", "path");
    el.id = nameToId(k);
    el.setAttribute('readableName', k);
    el.setAttribute('stroke-width', 5);
    el.setAttribute('fill', colors[k]);
    el.setAttribute('stroke-linejoin', 'round');
    el.setAttribute('d', 'M 11445 4535 z');
    // TODO(danvk): use jquery SVG to do this?
    el.onmouseover = countryMouseOver;
    el.onmouseout = countryMouseOut;
    document.getElementById('ctry').appendChild(el);
  }
  $('#svg-holder').mousedown(function(e) {
    console.log('down');
    pressViewer(viewer, e);
    $(this).mousemove(function(e) {
      moveViewer(viewer, e);
      console.log('move');
    }).mouseup(function(e) {
      releaseViewer(e);
      console.log('up');
      $(this).off('mousemove').off('mouseup');
    });
  });

  $('#slider').slider({
    range: false,
    value: -100,
    min: min,
    max: end_year,
    slide: function(e, ui) {
      slideToYear(ui.value);
    }
    // change: function(event, ui) {
    //   // ...
    // }
  });

  slideToYear(-100);
});

function makeSvgMatchImageViewer(xy) {
  // These coords are relative to the top-left corner of the un-tiled overlay.
  var x = xy.x, y = xy.y;
  // console.log(x, y);

  var zoom = viewer.dimensions.zoomLevel;
  var zoomPow = Math.pow(2, zoom - 7);
  x = x - (kExpandedBackgroundSize - kOriginalBackgroundWidth)/2 * zoomPow;
  y = y - (kExpandedBackgroundSize - kOriginalBackgroundHeight)/2 * zoomPow;
  x = -x;
  y = -y;

  // These coordinates are in the original SVG space.
  // console.log('translate: ' + x + ', ' + y + '  scale: ' + zoomPow);
  $("#ctry").attr("transform", "translate(" + x + "," + y + ") scale(" + zoomPow + ")");
}
