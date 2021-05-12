(function(exports) {
"use strict";

var delay_scale = 0.7;
var timer = null;

var animate = function(img, timeline, element, ratio) {
	var run_time = 0,
		i = 0,
		j;

	for (j = 0; j < timeline.length - 1; ++j) {
		run_time += timeline[j].delay;
	}

	var f = function() {
		var frame = i++ % timeline.length,
			delay = timeline[frame].delay * delay_scale,
			blits = timeline[frame].blit,
			ctx = element.getContext('2d');

		for (j = 0; j < blits.length; ++j) {
			var blit = blits[j],
				sx = blit[0] * ratio,
				sy = blit[1] * ratio,
				w = blit[2] * ratio,
				h = blit[3] * ratio,
				dx = blit[4] * ratio,
				dy = blit[5] * ratio;

			ctx.drawImage(img, sx, sy, w, h, dx, dy, w, h);
		}

		timer = window.setTimeout(f, delay);
	};

	if (timer) window.clearTimeout(timer);
	f();
};

var animate_fallback = function(img, timeline, element, ratio) {
	var run_time = 0,
		i = 0,
		j;

	for (j = 0; j < timeline.length - 1; ++j) {
		run_time += timeline[j].delay;
	}

	var f = function() {
		if (i % timeline.length === 0) {
			while (element.hasChildNodes()) {
				element.removeChild(element.lastChild);
			}
		}

		var frame = i++ % timeline.length,
			delay = timeline[frame].delay * delay_scale,
			blits = timeline[frame].blit;

		for (j = 0; j < blits.length; ++j) {
			var blit = blits[j],
				sx = blit[0],
				sy = blit[1],
				w = blit[2],
				h = blit[3],
				dx = blit[4],
				dy = blit[5];

			var d = document.createElement('div');
			d.style.position = 'absolute';
			d.style.left = dx + "px";
			d.style.top = dy + "px";
			d.style.width = w + "px";
			d.style.height = h + "px";
			d.style.backgroundImage = "url('" + img.src + "')";
			d.style.backgroundSize = (img.width / ratio) + "px " + (img.height / ratio) + "px";
			d.style.backgroundPosition = "-" + sx + "px -" + sy + "px";

			element.appendChild(d);
		}

		timer = window.setTimeout(f, delay);
	};

	if (timer) window.clearTimeout(timer);
	f();
};

exports.set_animation = function(img_url, timeline, canvas_id, fallback_id) {
	var i, j,
		auto = 1,
		devicePixelRatio = !auto || window.devicePixelRatio || 1,
		width = 0,
		height = 0,
		img = new Image(),
		final_img_url;
	// Find out what is the biggest blit:
	for (i = 0; i< timeline.length; i++) {
		for (j = 0; j < timeline[i].blit.length; j++) {
			var blit = timeline[i].blit[j],
				_width = blit[2] + blit[4],
				_height = blit[3] + blit[5];
			if (width < _width) width = _width;
			if (height < _height) height = _height;
		}
	}
	img.onload = function() {
		var canvas = document.getElementById(canvas_id);
		if (canvas && canvas.getContext) {
			var ctx = canvas.getContext('2d'),
				backingStoreRatio = !auto ||
									ctx.webkitBackingStorePixelRatio ||
									ctx.mozBackingStorePixelRatio ||
									ctx.msBackingStorePixelRatio ||
									ctx.oBackingStorePixelRatio ||
									ctx.backingStorePixelRatio || 1,
				ratio = devicePixelRatio / backingStoreRatio;
			canvas.width = width * ratio;
			canvas.height = height * ratio;
			canvas.style.width = width + 'px';
			canvas.style.height = height + 'px';
			// ctx.scale(ratio, ratio);
			animate(img, timeline, canvas, ratio);
		} else {
			var element = document.getElementById(fallback_id);
			element.style.width = width + 'px';
			element.style.height = height + 'px';
			element.style.position = 'relative';
			animate_fallback(img, timeline, element, devicePixelRatio);
		}
	};

	img.onerror = function() {
		if (devicePixelRatio != 1) {
			devicePixelRatio = 1;
			final_img_url = img_url;
			auto = 0;
			img.src = final_img_url;
		}
	};

	if (devicePixelRatio != 1) {
		var retinaImageSuffix = '@' + devicePixelRatio + 'x',
			regexMatch = /\.\w+$/;
		final_img_url = img_url.replace(regexMatch, function(match) { return retinaImageSuffix + match; });
	} else {
		final_img_url = img_url;
	}
	img.src = final_img_url;
};

})(window);
