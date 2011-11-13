var error_message = "An error occured on the server.  Administrators have been notified, and the issue will be resolved as soon as possible.";

function find(list, callback){
	al = $(list).toArray()
	for(var i in al){
		var element = $(al[i]);
		if(callback(element)){
			return element;
		}
	}
}

function find_with_text(list, text){
	return find(list, function(element){
		return element.text() == text;
	});
}

/* submitForm
 *
 * submits the form argument to the url argument using ajax.
 */
var loader = $("<img src='/site_media/pics/ajax-loader-small.gif' class='loader' />");
function submitForm(args){
	var success = args.success;
	var invalid = args.invalid;
	var on_complete = args.complete;
	var error = args.error;
	var form = args.form;

	form.find("input[type='submit']").after(loader);

	$.ajax({
		type: 'post',
		url: args.url,
		data: form.serialize(),
		success: function(response){
			if(response.success){
				$.each($(form).find("[class$='-error']"), function(i, error){
					$(error).text("");
				});
				success(response);
			}else{
				invalid(response);
			}
		},
		complete: function(){
			form.find(".loader").remove();
			if(on_complete){
				on_complete();
			}
		},
		error: function(XMLHttpRequest, textStatus, errorThrown){
		   error(textStatus, errorThrown);
		},
		dataType: "json"
	});
}

//bulletin js
function create_bulletin(bulletin){
	var bulletin_html = $("<li>").addClass("bulletin");
	bulletin_html.append($("<p>").addClass("bulletin-title").text(bulletin.title));
	
	bulletin_html.append($("<span>").addClass("bulletin-id").text(bulletin.id));
	bulletin_html.append($("<span>").addClass("bulletin-user").text(bulletin.user));
	bulletin_html.append($("<span>").addClass("bulletin-date").text(bulletin.date));
	bulletin_html.append($("<p>").addClass("bulletin-text").text(bulletin.text));
	
	$("<ul>").addClass("comment-list").appendTo(bulletin_html);
	
	var comment_container = $("<div>").addClass("comment-form-container");
	var comment_form = $("<form>").addClass("comment-form");
	
	var field_container = $("<div>").addClass("field-container");
	field_container.append("<textarea name='text' class='bulletin-comment-text'></textarea>");
	field_container.append("<span class='comment-text-error'></span>");
	field_container.append("<div><input class='submit-comment' type='submit' value='Comment' /></div>");
	field_container.append("<input type='hidden' name='bulletin_id' value='" + bulletin.id + "' />");
	
	comment_form.append(field_container);
	comment_container.append(comment_form);
	
	
	bulletin_html.append(comment_container);
	
	return bulletin_html;
}

function create_comment(comment){
	var comment_html = $("<li>").addClass("comment");
	
	comment_html.append($("<span>").addClass("comment-id").text(comment.id));
	comment_html.append($("<span>").addClass("comment-user").text(comment.user));
	comment_html.append($("<p>").addClass("comment-text").text(comment.text));
	comment_info = $("<div>").addClass("comment-info");
	comment_info.append($("<span>").addClass("comment-date").text(comment.date));
	comment_html.append(comment_info);
	
	return comment_html;
}

function load_bulletin_data(section){
	$.ajax({
		type: 'get',
		url: "bulletins/",
		cache: false,
		success: function(board){
			var bulletin_list = $(document).find(".bulletin-list");

			for(var x in board.bulletins){
				var bulletin_data = board.bulletins[x];

				var bulletin = create_bulletin(bulletin_data);
				var comment_list = bulletin.find(".comment-list");
				for(var i in bulletin_data.comments){
					var comment_data = bulletin_data.comments[i];
					create_comment(comment_data).appendTo(comment_list);
				}
				bulletin.appendTo(bulletin_list);

			}

			$(section).find(".bulletin-loading").remove();

			bulletin_list.slideDown('slow');
		},
		error: function(XMLHttpRequest, textStatus, errorThrown){
		   alert(error_message);
		},
		complete: function(){
			$(section).find(".ajax-call-loading").remove();
		},
		dataType: "json"
	});
}

function number_for_category(category){
	if(category == "Today"){
		return 0;
	}else if(category == "Tomorrow"){
		return 1;
	}else if(category == "This week"){
		return 2;
	}else if(category == "Next week"){
		return 3;
	}else if(category == "In a couple weeks"){
		return 4;
	}else if(category == "This year"){
		return 5;
	}else if(category == "In a while"){
		return 6;
	}else{
		return 7;
	}
}

function load_upcoming_data(elem, link){
	var element = $(elem);
	
	var url = link;
	if(url == null){
		url = "upcoming/";
	}

	$.ajax({
		type: "get",
		url: url,
		cache: false,
		success: function(response){
			if(response == null || response.length == 0){
				var no_upcoming = $("<span class='no-upcoming'>No upcoming assignments</span>");
				element.append(no_upcoming);
				return;
			}
					
			response_string = "";
			for(i=0; i<response.length; i++){
				response_string += response[i].category;
			}
			
			var upcoming_list = $("<ul>").addClass("upcoming-assignments");
			var current_category = $("<li>");
			for(i=0; i<response.length; i++){
				var assignment = response[i];
								
				if(assignment.category != current_category.find(".upcoming-category-header").text()){
					current_category = $("<li>").addClass("upcoming-category");
					current_category.append($("<span>").addClass("upcoming-category-header").text(assignment.category));
					current_category.append($("<ul>").addClass("upcoming-category-assignments"));
					upcoming_list.append(current_category);
				}
				
				var assignment_list = current_category.find(".upcoming-category-assignments");
				
				//create assignment
				var assignment_element = $("<li>").addClass("upcoming-assignment");
				assignment_element.append($("<a>").addClass("upcoming-assignment-name").attr("href", assignment.url).text(assignment.name));
				assignment_element.append($("<span>").addClass("upcoming-assignment-time").text(assignment.due_date));
				
				assignment_list.append(assignment_element);
			}
			
			element.append(upcoming_list);
			
		},
		error: function() {
			alert(error_message);
		},
		complete: function(){
			element.find(".ajax-call-loading").remove();
		},
		dataType: "json"
	});
}

function get_grade(element){
	element = $(element);
	
	$.ajax({
		type: "get",
		url: "grade/",
		cache: false,
		success: function(response){
			if(response.letter_grade == ""){
				element.append($("<span>").addClass("no-grade").text("Could not determine grade"));
			}else{
				element.append($("<p>").addClass("letter-grade").text(response.letter_grade));
				element.append($("<p>").addClass("grade-percent").text("(" + response.percent + "%" + ")"));
			}
		},
		error: function(){
			alert(error_message);
		},
		complete: function(){
			element.find(".small-ajax-loader").remove();
		},
		dataType: "json"
	});
}

function grade_display(user){
	return user.letter_grade + " (" + user.grade + "%)";
}

function average_grade_display(data){
	var display = $("<span>");
	display.addClass("average-grade-display");
	
	display.append(grade_display(data));
	
	return display;
}

function display_average_grades(){
	$.ajax({
		url: "average/",
		cache: false,
		success: function(response){
			$.each(response, function(i, assignment){
				var assignment_display = find_with_text($(".assignment-name"), assignment.name).parents(".assignment");
				
				var group = assignment_display.parents(".group");
				if(!group.find(".average-header").is(":visible")){
					$("<span class='average-header'>Average</span>").insertBefore(group.find(".assignment-list"));
				}
				
				assignment_display.append(average_grade_display(assignment.average));
				
				if(assignment.student){
					assignment_display.append(average_grade_display(assignment.student));
					
					if(!group.find(".you-header").is(":visible")){
						$("<span class='you-header'>You</span>").insertAfter(group.find(".average-header"));
					}
				}
			});
		},
		error: function(request, textStatus, errorThrown){
		
		},
		dataType: "json"
	});
}

function delete_bulletin_or_comment(type, args){
	var url = args.url;
	var success = args.success;
	
	$.ajax({
		type: "POST",
		url: url, 
		success: function(response){
			if(response.success){
				success(response);
			}else{
				alert("There was a problem deleting this " + type + ".  Refresh the page, and try again.");
			}
		},
		error: function(request, textStatus, errorThrown){
			alert(error_message);
		},
		dataType: "json"
	});
}

$(".bulletin").live("mouseenter", function(){
	var bulletin = $(this);
	var admin_status = $(".user-is-admin-or-staff").text();
	
	var username = $(".user-name").text();
	var bulletin_username = bulletin.find(".bulletin-user").text();
	
	if(username == bulletin_username || admin_status == "True"){
		if(!bulletin.find(".delete-bulletin").is(":visible")){ //delete link is not visible
			var bulletin_id = bulletin.find(".bulletin-id").text();
			bulletin.prepend("<a class='delete-bulletin' href=''>Delete</a>");
		}
	}
});

$(".bulletin").live("mouseleave", function(){
	$(this).find(".delete-bulletin").remove();
});

function delete_comment(args){
	delete_bulletin_or_comment("comment", args);
}

$(".comment").live("mouseenter", function(){
	var comment = $(this);
	var admin_status = $(".user-is-admin-or-staff").text();
	
	var username = $(".user-name").text();
	var comment_username = comment.find(".comment-user").text();
	
	if(username == comment_username || admin_status == "True"){
		if(!comment.find(".delete-comment").is(":visible")){ //delete link is not visible
			comment.find(".comment-info").append("<a class='delete-comment' href=''>delete</a>");
		}
	}
});

$(".comment").live("mouseleave", function(){
	$(this).find(".delete-comment").remove();
});

function delete_comment(args){
	delete_bulletin_or_comment("comment", args);
}

var message_display_time = 2000
$(document).ready(function(){
	var messages = $(".messages");
	
	if(messages.is(":visible")){
		setTimeout(function(){
			messages.slideUp();
		}, message_display_time);
	}
});

function adjust_course_menu(){
	var course_tabs = $(document.getElementById("course-tabs"));
	
	var right_header = course_tabs.parents(".header-right");
	var image_width = $(document.getElementById("tabs-menu-image")).outerWidth(true);
	
	if(image_width == 0){
		image_width = 13;
	}
	
	var container_width = right_header.width() - image_width - 13;
	
	var tabs = course_tabs.children();
	tabs.show();
	
	var extra_tabs = $(document.getElementById("extra-tabs"));
	extra_tabs.children().remove();
	
	var current_width = 0;
	for(var x=0; x<tabs.length; x++){
		tab = $(tabs[x]);
		
		current_width += tab.outerWidth(true) + 10;
		
		if(current_width >= container_width){
			tab.hide();
			
			var link = tab.html();
			extra_tabs.append(link);
		}
	}
	
	course_tabs.width(container_width);
}

/* Menu Script */

$(window).load(function(){
	adjust_course_menu();
});

var prevWidth;
$(window).resize(function(){
	var width = $(this).width();
	if(width == prevWidth){
		return;
	}
	prevWidth = width;
	
	adjust_course_menu();
});

$(document).ready(function(){
	var extra_tabs = $("#extra-tabs");
	extra_tabs.offset({ top: 100, left: 100 }); //fix ie bug, where position is not set
	
	var cover = $("#menu-clear-cover");
	cover.offset({ top: 100, left: 100 });
	cover.width(extra_tabs.width());
	cover.css('opacity', '0.0');
});

$("#tabs-menu-image").live('mouseenter mouseleave', function(event){
	var menu_image = $(this);
	var extra_tabs = $("#extra-tabs");
	
	if(extra_tabs.children().length == 0){
		return;
	}
	
	var cover = $("#menu-clear-cover");
	
	if(event.type == "mouseenter"){
		extra_tabs.show();
		cover.show();
				
		var offset = menu_image.offset();
		
		var tabs_width = extra_tabs.width();
		
		//position list
		var top_position = (offset.top + menu_image.outerHeight());
		var left_position = (offset.left - tabs_width + menu_image.width());
		extra_tabs.offset({ top: top_position, left: left_position });
		
		cover.offset({ top: offset.top, left: left_position });
	}else{
		extra_tabs.hide();
		cover.hide();
	}
});

function make_show_hide_link(link, click_callback){
	var qlink = $(link);
	var text = qlink.text();
	
	qlink.livequery('click', function(){
		if($(this).text() == text){
			$(this).text("Hide");
			click_callback(true);
		}else{
			$(this).text(text);
			click_callback(false);
		}
		
		return false;
	});
}

function display_errors(form, errors){
	var f = $(form);
	
	$.each(errors, function(field, error){
		f.find("." + field + "-error").text(error);
	});
}

/* Fix for new csrf ajax vulnerability. */
$.ajaxSetup({
	beforeSend: function(xhr, settings) {
		function getCookie(name) {
			var cookieValue = null;
			if(document.cookie && document.cookie != ''){
				var cookies = document.cookie.split(';');
				for(var i=0; i < cookies.length; i++){
					var cookie = jQuery.trim(cookies[i]);
					// Does this cookie string begin with the name we want?
					if (cookie.substring(0, name.length + 1) == (name + '=')) {
						cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
						break;
					}
				}
			}
			
			return cookieValue;
		}
		
		if(!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
			//Only send the token to relative URLs i.e. locally.
			xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
		}
	}
});

/* Allow Color Animations in jQuery */
(function(jQuery){jQuery.each(['backgroundColor','borderBottomColor','borderLeftColor','borderRightColor','borderTopColor','color','outlineColor'],function(i,attr){jQuery.fx.step[attr]=function(fx){if(fx.state==0){fx.start=getColor(fx.elem,attr);fx.end=getRGB(fx.end)}fx.elem.style[attr]="rgb("+[Math.max(Math.min(parseInt((fx.pos*(fx.end[0]-fx.start[0]))+fx.start[0]),255),0),Math.max(Math.min(parseInt((fx.pos*(fx.end[1]-fx.start[1]))+fx.start[1]),255),0),Math.max(Math.min(parseInt((fx.pos*(fx.end[2]-fx.start[2]))+fx.start[2]),255),0)].join(",")+")"}});function getRGB(color){var result;if(color&&color.constructor==Array&&color.length==3)return color;if(result=/rgb\(\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*\)/.exec(color))return[parseInt(result[1]),parseInt(result[2]),parseInt(result[3])];if(result=/rgb\(\s*([0-9]+(?:\.[0-9]+)?)\%\s*,\s*([0-9]+(?:\.[0-9]+)?)\%\s*,\s*([0-9]+(?:\.[0-9]+)?)\%\s*\)/.exec(color))return[parseFloat(result[1])*2.55,parseFloat(result[2])*2.55,parseFloat(result[3])*2.55];if(result=/#([a-fA-F0-9]{2})([a-fA-F0-9]{2})([a-fA-F0-9]{2})/.exec(color))return[parseInt(result[1],16),parseInt(result[2],16),parseInt(result[3],16)];if(result=/#([a-fA-F0-9])([a-fA-F0-9])([a-fA-F0-9])/.exec(color))return[parseInt(result[1]+result[1],16),parseInt(result[2]+result[2],16),parseInt(result[3]+result[3],16)];return colors[jQuery.trim(color).toLowerCase()]}function getColor(elem,attr){var color;do{color=jQuery.curCSS(elem,attr);if(color!=''&&color!='transparent'||jQuery.nodeName(elem,"body"))break;attr="backgroundColor"}while(elem=elem.parentNode);return getRGB(color)};var colors={aqua:[0,255,255],azure:[240,255,255],beige:[245,245,220],black:[0,0,0],blue:[0,0,255],brown:[165,42,42],cyan:[0,255,255],darkblue:[0,0,139],darkcyan:[0,139,139],darkgrey:[169,169,169],darkgreen:[0,100,0],darkkhaki:[189,183,107],darkmagenta:[139,0,139],darkolivegreen:[85,107,47],darkorange:[255,140,0],darkorchid:[153,50,204],darkred:[139,0,0],darksalmon:[233,150,122],darkviolet:[148,0,211],fuchsia:[255,0,255],gold:[255,215,0],green:[0,128,0],indigo:[75,0,130],khaki:[240,230,140],lightblue:[173,216,230],lightcyan:[224,255,255],lightgreen:[144,238,144],lightgrey:[211,211,211],lightpink:[255,182,193],lightyellow:[255,255,224],lime:[0,255,0],magenta:[255,0,255],maroon:[128,0,0],navy:[0,0,128],olive:[128,128,0],orange:[255,165,0],pink:[255,192,203],purple:[128,0,128],violet:[128,0,128],red:[255,0,0],silver:[192,192,192],white:[255,255,255],yellow:[255,255,0]}})(jQuery);

/* Allow forms to be submitted with 'live' binding */
(function($){$.extend($.fn,{livequery:function(type,fn,fn2){var self=this,q;if($.isFunction(type))fn2=fn,fn=type,type=undefined;$.each($.livequery.queries,function(i,query){if(self.selector==query.selector&&self.context==query.context&&type==query.type&&(!fn||fn.$lqguid==query.fn.$lqguid)&&(!fn2||fn2.$lqguid==query.fn2.$lqguid))return(q=query)&&false});q=q||new $.livequery(this.selector,this.context,type,fn,fn2);q.stopped=false;q.run();return this},expire:function(type,fn,fn2){var self=this;if($.isFunction(type))fn2=fn,fn=type,type=undefined;$.each($.livequery.queries,function(i,query){if(self.selector==query.selector&&self.context==query.context&&(!type||type==query.type)&&(!fn||fn.$lqguid==query.fn.$lqguid)&&(!fn2||fn2.$lqguid==query.fn2.$lqguid)&&!this.stopped)$.livequery.stop(query.id)});return this}});$.livequery=function(selector,context,type,fn,fn2){this.selector=selector;this.context=context||document;this.type=type;this.fn=fn;this.fn2=fn2;this.elements=[];this.stopped=false;this.id=$.livequery.queries.push(this)-1;fn.$lqguid=fn.$lqguid||$.livequery.guid++;if(fn2)fn2.$lqguid=fn2.$lqguid||$.livequery.guid++;return this};$.livequery.prototype={stop:function(){var query=this;if(this.type)this.elements.unbind(this.type,this.fn);else if(this.fn2)this.elements.each(function(i,el){query.fn2.apply(el)});this.elements=[];this.stopped=true},run:function(){if(this.stopped)return;var query=this;var oEls=this.elements,els=$(this.selector,this.context),nEls=els.not(oEls);this.elements=els;if(this.type){nEls.bind(this.type,this.fn);if(oEls.length>0)$.each(oEls,function(i,el){if($.inArray(el,els)<0)$.event.remove(el,query.type,query.fn)})}else{nEls.each(function(){query.fn.apply(this)});if(this.fn2&&oEls.length>0)$.each(oEls,function(i,el){if($.inArray(el,els)<0)query.fn2.apply(el)})}}};$.extend($.livequery,{guid:0,queries:[],queue:[],running:false,timeout:null,checkQueue:function(){if($.livequery.running&&$.livequery.queue.length){var length=$.livequery.queue.length;while(length--)$.livequery.queries[$.livequery.queue.shift()].run()}},pause:function(){$.livequery.running=false},play:function(){$.livequery.running=true;$.livequery.run()},registerPlugin:function(){$.each(arguments,function(i,n){if(!$.fn[n])return;var old=$.fn[n];$.fn[n]=function(){var r=old.apply(this,arguments);$.livequery.run();return r}})},run:function(id){if(id!=undefined){if($.inArray(id,$.livequery.queue)<0)$.livequery.queue.push(id)}else $.each($.livequery.queries,function(id){if($.inArray(id,$.livequery.queue)<0)$.livequery.queue.push(id)});if($.livequery.timeout)clearTimeout($.livequery.timeout);$.livequery.timeout=setTimeout($.livequery.checkQueue,20)},stop:function(id){if(id!=undefined)$.livequery.queries[id].stop();else $.each($.livequery.queries,function(id){$.livequery.queries[id].stop()})}});$.livequery.registerPlugin('append','prepend','after','before','wrap','attr','removeAttr','addClass','removeClass','toggleClass','empty','remove');$(function(){$.livequery.play()});var init=$.prototype.init;$.prototype.init=function(a,c){var r=init.apply(this,arguments);if(a&&a.selector)r.context=a.context,r.selector=a.selector;if(typeof a=='string')r.context=c||document,r.selector=a;return r};$.prototype.init.prototype=$.prototype})(jQuery);

/*
 * Date Format 1.2.3
 * (c) 2007-2009 Steven Levithan <stevenlevithan.com>
 * MIT license
 *
 * Includes enhancements by Scott Trenda <scott.trenda.net>
 * and Kris Kowal <cixar.com/~kris.kowal/>
 *
 * Accepts a date, a mask, or a date and a mask.
 * Returns a formatted version of the given date.
 * The date defaults to the current date/time.
 * The mask defaults to dateFormat.masks.default.
 */

var dateFormat = function () {
	var	token = /d{1,4}|m{1,4}|yy(?:yy)?|([HhMsTt])\1?|[LloSZ]|"[^"]*"|'[^']*'/g,
	timezone = /\b(?:[PMCEA][SDP]T|(?:Pacific|Mountain|Central|Eastern|Atlantic) (?:Standard|Daylight|Prevailing) Time|(?:GMT|UTC)(?:[-+]\d{4})?)\b/g,
	timezoneClip = /[^-+\dA-Z]/g,
	pad = function (val, len) {
	val = String(val);
	len = len || 2;
	while (val.length < len) val = "0" + val;
	return val;
	};
	
	// Regexes and supporting functions are cached through closure
	return function (date, mask, utc) {
	var dF = dateFormat;
	
	// You can't provide utc if you skip other args (use the "UTC:" mask prefix)
	if (arguments.length == 1 && Object.prototype.toString.call(date) == "[object String]" && !/\d/.test(date)) {
	mask = date;
	date = undefined;
	}
	
	// Passing date through Date applies Date.parse, if necessary
	date = date ? new Date(date) : new Date;
	if (isNaN(date)) throw SyntaxError("invalid date");
	
	mask = String(dF.masks[mask] || mask || dF.masks["default"]);
	
	// Allow setting the utc argument via the mask
	if (mask.slice(0, 4) == "UTC:") {
	mask = mask.slice(4);
	utc = true;
	}
	
	var	_ = utc ? "getUTC" : "get",
	d = date[_ + "Date"](),
	D = date[_ + "Day"](),
	m = date[_ + "Month"](),
	y = date[_ + "FullYear"](),
	H = date[_ + "Hours"](),
	M = date[_ + "Minutes"](),
	s = date[_ + "Seconds"](),
	L = date[_ + "Milliseconds"](),
	o = utc ? 0 : date.getTimezoneOffset(),
	flags = {
	d:    d,
	dd:   pad(d),
	ddd:  dF.i18n.dayNames[D],
	dddd: dF.i18n.dayNames[D + 7],
	m:    m + 1,
	mm:   pad(m + 1),
	mmm:  dF.i18n.monthNames[m],
	mmmm: dF.i18n.monthNames[m + 12],
	yy:   String(y).slice(2),
	yyyy: y,
	h:    H % 12 || 12,
	hh:   pad(H % 12 || 12),
	H:    H,
	HH:   pad(H),
	M:    M,
	MM:   pad(M),
	s:    s,
	ss:   pad(s),
	l:    pad(L, 3),
	L:    pad(L > 99 ? Math.round(L / 10) : L),
	t:    H < 12 ? "a"  : "p",
	tt:   H < 12 ? "am" : "pm",
	T:    H < 12 ? "A"  : "P",
	TT:   H < 12 ? "AM" : "PM",
	Z:    utc ? "UTC" : (String(date).match(timezone) || [""]).pop().replace(timezoneClip, ""),
	o:    (o > 0 ? "-" : "+") + pad(Math.floor(Math.abs(o) / 60) * 100 + Math.abs(o) % 60, 4),
	S:    ["th", "st", "nd", "rd"][d % 10 > 3 ? 0 : (d % 100 - d % 10 != 10) * d % 10]
	};
	
	return mask.replace(token, function ($0) {
	return $0 in flags ? flags[$0] : $0.slice(1, $0.length - 1);
	});
	};
	}();
	
	// Some common format strings
	dateFormat.masks = {
	"default":      "ddd mmm dd yyyy HH:MM:ss",
	shortDate:      "m/d/yy",
	mediumDate:     "mmm d, yyyy",
	longDate:       "mmmm d, yyyy",
	fullDate:       "dddd, mmmm d, yyyy",
	shortTime:      "h:MM TT",
	mediumTime:     "h:MM:ss TT",
	longTime:       "h:MM:ss TT Z",
	isoDate:        "yyyy-mm-dd",
	isoTime:        "HH:MM:ss",
	isoDateTime:    "yyyy-mm-dd'T'HH:MM:ss",
	isoUtcDateTime: "UTC:yyyy-mm-dd'T'HH:MM:ss'Z'"
	};
	
	// Internationalization strings
	dateFormat.i18n = {
	dayNames: [
	"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat",
	"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
	],
	monthNames: [
	"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
	"January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"
	]
	};
	
	// For convenience...
	Date.prototype.format = function (mask, utc) {
	return dateFormat(this, mask, utc);
};

/* Fix for IE fadeIn problem */
(function($) {
	$.fn.customFadeIn = function(speed, callback) {
		$(this).fadeIn(speed, function() {
			if(!$.support.opacity)
				$(this).get(0).style.removeAttribute('filter');
			if(callback != undefined)
				callback();
		});
	};
	$.fn.customFadeOut = function(speed, callback) {
		$(this).fadeOut(speed, function() {
			if(!$.support.opacity)
				$(this).get(0).style.removeAttribute('filter');
			if(callback != undefined)
				callback();
		});
	};
	$.fn.customFadeTo = function(speed,to,callback) {
		return this.animate({opacity: to}, speed, function() {
			if (to == 1 && jQuery.browser.msie)
				this.style.removeAttribute('filter');
			if (jQuery.isFunction(callback))
				callback();
		});
	};
})(jQuery);	
