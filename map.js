var min = -400;
var max = end_year;  // comes from several_countries.js
var kExpandedBackgroundSize = 32768;
var kOriginalBackgroundWidth = 25201;
var kOriginalBackgroundHeight = 15120;

// startX/Y are in the fully-zoomed SVG coordinate system.
var startX = 12100;
var startY = 3550;
var startZoom = 5;
var maxZoom = Math.log(kExpandedBackgroundSize / 256) / Math.log(2);

function nameToId(name) {
  return name.replace(/ /g, '_');
}

function countryMouseOver(e) {
  // var x = e.pageX, y = e.pageY;
  $('#highlighted-country').html(e.target.getAttribute('readableName'));
  // $('#highlighted-country').offset({ top: y + 20, left: x - 50 })
  // var centerOfMass = computeCenterOfMass(e.target);
  // console.log(centerOfMass);
  // $('#highlighted-country').offset({
  //   top: centerOfMass.y,
  //   left: centerOfMass.x
  // });

  // TODO(danvk): use the center of mass, but transform to screen coords.
  var r = e.target.getBoundingClientRect();
  $('#highlighted-country').offset({
    top: 0.5 * (r.top + r.bottom),
    left: 0.5 * (r.left + r.right)
  });
  
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

  // XXX This logic is correct for moving forward, but not backwards.
  // If a country disappears when you go forward one year, this will not make
  // it reappear when you move back one year.
  // Additionally, there are off-by-one errors going forward/backward.
  var cum_delta = {};
  var sgn = this_year_idx - last_drawn_idx < 0 ? -1 : +1;
  for (var i = last_drawn_idx; ; i += sgn) {
    if (rome[i] !== undefined) {
      var data = rome[i][1];
      for (var k in data) {
        cum_delta[k] = data[k];
      }
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
  // From http://stackoverflow.com/questions/2132172/disable-text-highlighting-on-double-click-in-jquery
  $.extend($.fn.disableTextSelect = function() {
    return this.each(function(){
      if ($.browser.mozilla) {  //Firefox
        $(this).css('MozUserSelect','none');
      } else if ($.browser.msie) {  //IE
        $(this).bind('selectstart',function(){return false;});
      } else {  //Opera, etc.
        $(this).mousedown(function(){return false;});
      }
    });
  });

  var setAttrs = function(el, obj) {
    $.each(obj, function(k, v) {
      el.setAttribute(k, v);
    });
  };

  var $svgHolder = $('#svg-holder');
  var svgNS = "http://www.w3.org/2000/svg";
  var svg = document.createElementNS(svgNS, "svg");
  setAttrs(svg, {
    "id": "svg-el",
    "width": $svgHolder.width(),
    "height": $svgHolder.height()
  });
  var ctryG = document.createElementNS(svgNS, "g");
  setAttrs(ctryG, {
    'id': 'ctry',
    'stroke': '#999999',
    'stroke-width': '1',
    'stroke-miterlimit': '1',
    'stroke-linejoin': 'round',
    'stroke-linecap': 'round'
  });

  svg.appendChild(ctryG);
  $svgHolder.append(svg);

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
    ctryG.appendChild(el);
  }

  var scroll_amount = 0;
  $('#svg-holder')
    .mousedown(function(e) {
      pressViewer(viewer, e);
      $(document).mousemove(function(e) {
        moveViewer(viewer, e);
      }).mouseup(function(e) {
        releaseViewer(e);
        $(this).off('mousemove').off('mouseup');
      });
    })
    .dblclick(function(e) {
      var mouse = localizeCoordinates(viewer, {'x': e.clientX, 'y': e.clientY});
      zoomImage(viewer, mouse, +1);
    })
    .disableTextSelect()
    .mousewheel(function(e, delta) {
      var old_amount = scroll_amount;
      scroll_amount += delta;
      if (Math.abs(scroll_amount) > 2.0) {
        var mouse = localizeCoordinates(viewer, {'x': e.clientX, 'y': e.clientY});
        var direction = (scroll_amount > 0 ? +1 : -1);
        scroll_amount = 0;
        zoomImage(viewer, mouse, direction);
      }
    });

  $('svg').on('click', function(e) {
    e.preventDefault();
    var svg = e.currentTarget;
    var g = $(svg).find('g').get(0)
    var pt = svg.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    var svgPt = pt.matrixTransform(g.getScreenCTM().inverse());
    console.log(svgPt);
  });

  // this prevents the "page bounce" effect in Safari/Chrome on Lion.
  $(document).mousewheel(function(e) {
    e.preventDefault();
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
  x = (kExpandedBackgroundSize - kOriginalBackgroundWidth)/2 * zoomPow - x;
  y = (kExpandedBackgroundSize - kOriginalBackgroundHeight)/2 * zoomPow - y;

  // These coordinates are in the original SVG space.
  // console.log('translate: ' + x + ', ' + y + '  scale: ' + zoomPow);
  $("#ctry").attr("transform", "translate(" + x + "," + y + ") scale(" + zoomPow + ")");
}

// Compute the center of mass of an SVG <path> element.
// This approximates the path with a 10,000-sided polygon.
// Returns an { area: ..., x: ..., y: ...} object.
function computeCenterOfMass(path, numSamples) {
  if (!numSamples) numSamples = 1000;

  var step = path.getTotalLength() / numSamples;
  var A = 0;  // area
  var cx = 0, cy = 0;  // centroid

  // pt_i = point at step i, pt_im1 = point at step (i - 1)
  var pt_im1 = path.getPointAtLength(-step);
  for (var i = 0; i < numSamples; i++) {
    var pt_i = path.getPointAtLength(i * step);

    var part = (pt_im1.x * pt_i.y - pt_i.x * pt_im1.y);
    A += part;
    cx += (pt_im1.x + pt_i.x) * part;
    cy += (pt_im1.y + pt_i.y) * part;

    pt_im1 = pt_i;
  }
  A /= 2.0;

  return {
    area: Math.abs(A),
    x: cx / (6.0 * A),
    y: cy / (6.0 * A)
  };
}
