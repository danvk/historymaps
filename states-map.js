var min = 1783;
var max = 1999;  // comes from several_countries.js
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
  
  e.target.setAttribute('stroke-width', 0.1);
}
function countryMouseOut(e) {
  $('#highlighted-country').html('');
  e.target.setAttribute('stroke-width', 0.05);
}

var last_drawn_idx = -1;
var shape_indices = {};  // name -> year index currently being displayed.

var shape_to_year_idx_map = {};
for (var i = 0; i < rome.length; i++) {
  var data = rome[i][1];
  for (var k in data) {
    if (!(k in shape_to_year_idx_map)) {
      shape_to_year_idx_map[k] = [i];
    } else {
      shape_to_year_idx_map[k].push(i);
    }
  }
}

function slideToYear(year) {
  var this_year_idx = 0;
  for (var i = 0; i < rome.length; i++) {
    if (rome[i][0] > year) {
      this_year_idx = i - 1;
      break;
    }
  }
  // console.log('slideToYear(' + year + '): ' + last_drawn_idx + ' -> ' + this_year_idx);

  // XXX This logic is correct for moving forward, but not backwards.
  // If a country disappears when you go forward one year, this will not make
  // it reappear when you move back one year.
  // Additionally, there are off-by-one errors going forward/backward.
  var cum_delta = {};
  var sgn = this_year_idx - last_drawn_idx < 0 ? -1 : +1;
  if (this_year_idx > last_drawn_idx) {
    // Move year forward.
    for (var i = last_drawn_idx; i <= this_year_idx; i++) {
      if (rome[i] === undefined) continue;
      var data = rome[i][1];
      for (var k in data) {
        cum_delta[k] = data[k];
        shape_indices[k] = i;
      }
    }
  } else {
    // Move year backward.
    for (var k in shape_indices) {
      // console.log(k + ' -> ' + shape_indices[k] + ' (' + rome[shape_indices[k]][0] + ')');
      if (shape_indices[k] > this_year_idx) {
        var indices = shape_to_year_idx_map[k];
        var cur_idx = indices.indexOf(shape_indices[k]);
        if (cur_idx <= 0) throw "ick!";
        
        while (indices[cur_idx] > this_year_idx) cur_idx--;
        var new_idx = indices[cur_idx];
        shape_indices[k] = new_idx;
        cum_delta[k] = rome[new_idx][1][k];
      }
    }
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

// Collects all currently-visible paths into a dict.
// Useful for testing.
function collectPaths() {
  var paths = {};
  for (var k in colors) {
    var d = $('#' + nameToId(k)).attr("d");
    if (d && d != "M 11445 4535 z") {
      paths[k] = d;
    }
  }
  return paths;
}

function areDictsEqual(a, b) {
  for (var k in a) {
    if (!(k in b)) return false;
    if (a[k] != b[k]) return false;
  }
  for (var k in b) {
    if (!(k in a)) return false;
  }
  return true;
}

function test() {
  var init1783 = collectPaths();
  // slideToYear(1800);
  // var init1800 = collectPaths();
  slideToYear(1810);
  // slideToYear(1800);
  // var final1800 = collectPaths();
  slideToYear(1783);
  var final1783 = collectPaths();
  console.log(init1783);
  console.log(final1783);
  if (!areDictsEqual(init1783, final1783)
     // || !areDictsEqual(init1800, final1800)
      ) {
    throw "Error";
  } else {
    console.log("good to go!");
  }
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

  // create paths for all empires/nations
  for (var k in colors) {
    var el = document.createElementNS("http://www.w3.org/2000/svg", "path");
    el.id = nameToId(k);
    el.setAttribute('readableName', k);
    el.setAttribute('stroke-width', 0.05);
    el.setAttribute('fill', colors[k]);
    el.setAttribute('stroke-linejoin', 'round');
    el.setAttribute('d', 'M 11445 4535 z');
    // TODO(danvk): use jquery SVG to do this?
    el.onmouseover = countryMouseOver;
    el.onmouseout = countryMouseOut;
    document.getElementById('ctry').appendChild(el);
  }

  var scroll_amount = 0;
  $('#svg-holder')
    .mousedown(function(e) {
      // pressViewer(viewer, e);
      $(document).mousemove(function(e) {
        // moveViewer(viewer, e);
      }).mouseup(function(e) {
        // releaseViewer(e);
        $(this).off('mousemove').off('mouseup');
      });
    })
    // .dblclick(function(e) {
    //   var mouse = localizeCoordinates(viewer, {'x': e.clientX, 'y': e.clientY});
    //   zoomImage(viewer, mouse, +1);
    // })
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

  // this prevents the "page bounce" effect in Safari/Chrome on Lion.
  $(document).mousewheel(function(e) {
    e.preventDefault();
  });

  $('#slider').slider({
    range: false,
    value: 1783,
    min: min,
    max: 1999,
    slide: function(e, ui) {
      slideToYear(ui.value);
    }
    // change: function(event, ui) {
    //   // ...
    // }
  });

  slideToYear(1783);
});

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
