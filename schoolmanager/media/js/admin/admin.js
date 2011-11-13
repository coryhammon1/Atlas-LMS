function get_username_from_display(display){
	var withParenthesis = new String(display.text().match(/\([^)]+\)/));
	return withParenthesis.substr(1, withParenthesis.length - 2);
}

function user_display_text_concat(display){
	var text = new String(display.text());
	
	var last_name = new String(text.match(/.+,/));
	var first_name = new String(text.match(/, .+\(/));
	var username = get_username_from_display(display);
	
	var concatenated = "";
	for(var i in text){
		var char = text.charAt(i);
		var m = char.match("[a-zA-Z0-9]");
		if(m){
			concatenated += m;
		}
	}
	
	return concatenated;
}

function user_text_display(user){
	return user.last_name + ", " + user.first_name + " (" + user.username + ")";
}

function make_user_display(user){
	var user_display = $("<a>");
	user_display.addClass("user-display");
	user_display.attr("href", "/siteadmin/users/" + user.id + "/");
	user_display.append(user_text_display(user));
	
	return user_display;
}

function create_user_list_display(users){
	var user_list = $("<ul>");
	user_list.addClass("user-list");
	
	for(var i in users){
		var user = users[i];
		
		var user_element = $("<li>");
		user_element.addClass("user-element");
		user_element.appendTo(user_list);
		
		var user_display = make_user_display(user);
		user_display.appendTo(user_element);
	}
	
	return user_list;
}

function create_course_display(course){
	var course_display = $("<li>");
	course_display.append("<a href='' class='enroll-course'>" + course.name + "</a>");
	course_display.append("<span class='course-id'>" + course.id + "</span>");
	return course_display;
}

function create_course_list_display(courses){
	var list = $("<ul>");
	list.addClass("course-list");
	
	for(var i in courses){
		var course = courses[i];
		list.append(create_course_display(course));
	}
	
	return list;
}

function make_course_link(course){
	var course_display = $("<li>");
	course_display.addClass("course");
	course_display.append("<a href='" + course.id + "/' class='course-link'>" + course.name + "</a>");
	course_display.append("<span class='course-id'>" + course.id + "</span>");
	return course_display;
}

function create_course_link_list(courses){
	var list = $("<ul>");
	list.addClass("course-list");
	
	for(var i in courses){
		var course = courses[i];
		list.append(make_course_link(course));
	}
	
	return list;
}

function make_tab(element){
	var tab_list = $(element);
	tab_list.find(".tab-content").hide();
}

function get_tab(tab_list, tab_text){	
	var tab_name = find_with_text($(tab_list).find(".tab-name"), tab_text);
	return tab_name.parents(".tab");
}

function getTabData(args){
	var tab = args.tab;
	var url = args.url;
	var get_data = args.get_data;
	var get_content = args.get_content;
	
	var tab_list = tab.parents(".tabbed-list");
	var tab_display = tab_list.find(".tab-display");
	var tab_content = tab.find(".tab-content");
	
	tab_display.empty();
	
	if(tab_content.children().length > 0){ //data was already loaded		
		tab_content.children().clone().appendTo(tab_display);
	}else{				//get data from server
		tab_display.append("<div class='ajax-call-loading'><img src='/site_media/pics/ajax-loader.gif' /></div>");
		
		$.ajax({
			url: url,
			data: get_data(), //get_data_callback
			dataType: "json",
			cache: false,
			success: function(response, textStatus, request){
				tab_display.empty();
								
				var content = get_content(response);
				tab_content.append(content);
				tab_display.append(content.clone());
			},
			complete: function(){
				tab_display.find("img").parent().remove();
			}
		});
	}
		
	tab_list.find(".tab").removeClass("current-tab");
	tab.addClass("current-tab");
}

function insert_into_list(args){
	var list = $(args.list);
	var new_ob = $(args.new_ob);
	var new_ob_val = args.new_ob_val;
	var get_val_callback = args.get_val;
	var comparison_callback = args.comparison;
	
	var ob_list = list.children().toArray();
	
	if(ob_list.length == 0){
		new_ob.appendTo(list);
	}else{
		for(i in ob_list){
			var check_ob = $(ob_list[i]);
			var insert = false;
			
			if(comparison_callback){
				insert = comparison_callback(new_ob, check_ob);
			}else{
				var check_val = get_val_callback(check_ob);
				insert = new_ob_val < check_val;
			}
			
			if(insert){
				new_ob.insertBefore(check_ob);
				break;
			}
			
			if(i == ob_list.length - 1){
				new_ob.insertAfter(check_ob);
			}
		}
	}
}