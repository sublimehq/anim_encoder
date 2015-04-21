(function(exports) {
"use strict";

var delay_scale = 0.7;
var timer = null;

var animate = function(img, timeline, element) {
	var i = 0;

	var run_time = 0;
	for (var j = 0; j < timeline.length - 1; ++j) {
		run_time += timeline[j].delay;
	}

	var f = function() {
		var frame = i++ % timeline.length;
		var delay = timeline[frame].delay * delay_scale;
		var blits = timeline[frame].blit;

		var ctx = element.getContext('2d');

		for (j = 0; j < blits.length; ++j) {
			var blit = blits[j];
			var sx = blit[0];
			var sy = blit[1];
			var w = blit[2];
			var h = blit[3];
			var dx = blit[4];
			var dy = blit[5];
			ctx.drawImage(img, sx, sy, w, h, dx, dy, w, h);
		}

		timer = window.setTimeout(f, delay);
	};

	if (timer) window.clearTimeout(timer);
	f();
};

var animate_fallback = function(img, timeline, element) {
	var i = 0;

	var run_time = 0;
	for (var j = 0; j < timeline.length - 1; ++j) {
		run_time += timeline[j].delay;
	}

	var f = function() {
		if (i % timeline.length === 0) {
			while (element.hasChildNodes()) {
				element.removeChild(element.lastChild);
			}
		}

		var frame = i++ % timeline.length;
		var delay = timeline[frame].delay * delay_scale;
		var blits = timeline[frame].blit;

		for (j = 0; j < blits.length; ++j) {
			var blit = blits[j];
			var sx = blit[0];
			var sy = blit[1];
			var w = blit[2];
			var h = blit[3];
			var dx = blit[4];
			var dy = blit[5];

			var d = document.createElement('div');
			d.style.position = 'absolute';
			d.style.left = dx + "px";
			d.style.top = dy + "px";
			d.style.width = w + "px";
			d.style.height = h + "px";
			d.style.backgroundImage = "url('" + img.src + "')";
			d.style.backgroundPosition = "-" + sx + "px -" + sy + "px";

			element.appendChild(d);
		}

		timer = window.setTimeout(f, delay);
	};

	if (timer) window.clearTimeout(timer);
	f();
};

exports.set_animation = function(img_url, timeline, canvas_id, fallback_id) {
	var img = new Image();
	img.onload = function() {
		var canvas = document.getElementById(canvas_id);
		if (canvas && canvas.getContext) {
			animate(img, timeline, canvas);
		} else {
			animate_fallback(img, timeline, document.getElementById(fallback_id));
		}
	};
	img.src = img_url;
};

})(window);
