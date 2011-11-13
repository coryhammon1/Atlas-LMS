function course_is_in_list(course, list){
	for(var i in list){
		var other = $(list[i]);
		var other_value = other.find(".course-name").text();
		
		if(course.name == other_value){
			return true;
		}
	}
	
	return false;
}

$(".tab").live('click', function(){
	var tab = $(this);
	
	getTabData({
		tab: tab,
		url: "../../courses/partial/",
		get_data: function(){
			var department = tab.find(".tab-name").text();
			var term = tab.parents(".course-term").find(".course-term-title").text();
			return { department: department, term: term }
		},
		get_content: function(response){
			var courses = response.courses;
			
			var filtered_courses = [];
			var user_courses = tab.parents(".course-term").find(".user-course-list").children().toArray();
			for(var i in courses){
				var course = courses[i];
				
				if(!course_is_in_list(course, user_courses)){
					filtered_courses.push(course);
				}
			}
			
			if(filtered_courses.length == 0){
				return $("<p class='no-courses'>There are no courses in this category.</p>");
			}else{
				return create_course_list_display(filtered_courses);
			}
		}
	});
	
	return false;
});


$(".enroll-course-menu").livequery('click', function(){
	var link = $(this);
	var term = link.parents(".course-term");
	var tab_list = term.find(".tabbed-courses");
	var link_text = "Add Course";
	
	if(link.text() == link_text){
		link.text("Hide");
		tab_list.slideDown('slow');
	}else{
		link.text(link_text);
		tab_list.slideUp('slow');
	}
		
	return false;
});

$(".enroll-course").live('click', function(){
	var course = $(this);
	var course_term = course.parents(".course-term");
	var course_list = course_term.find(".user-course-list");
	var course_id = course.parent().find(".course-id").text();
	
	$.ajax({
		url: "enroll/",
		type: "POST",
		data: { 'course_id': course_id },
		success: function(response){
			if(response.success){
				var new_course = response.course;
				var course_display = $("<li>");
				course_display.addClass("user-course");
				course_display.append($("<span class='course-id'>" + new_course.id + "</span>"));
				course_display.append($("<span class='course-name'>" + new_course.name + "</span>"));
				course_display.find(".course-name").hide();
				
				course.parent().fadeOut('slow', function(){
					insert_into_list({
						list: course_list,
						new_ob: course_display,
						new_ob_val: new_course.name,
						get_val: function(check_course){
							return check_course.find(".course-name").text();
						}
					});
					
					course_display.find(".course-name").customFadeIn('slow');
				});
				
				var tab_list = course.parents(".tabbed-list");
				var tab = get_tab(tab_list, response.course.department.toUpperCase());
				tab.find(".tab-content").empty();
			}else{
				alert("There was a problem adding this course.  Refresh the page, and try again.");
			}
		},
		error: function(request, textStatus, errorThrown){
			alert(error_message);
		},
		dataType: "json"
	});
	
	return false;
});

$(".user-course").livequery('mouseenter', function(){
	var course = $(this);
	
	if(!course.find(".course-menu").is(":visible")){
		var menu = $("<span class='course-menu'></span>");
		menu.append($("<a href='' class='remove-course'>remove</a>"));
		menu.appendTo(course);
	}
});

$(".user-course").livequery('mouseleave', function(){
	var course = $(this);
	course.find(".course-menu").remove();
});

$(".remove-course").livequery('click', function(){
	var course = $(this).parents(".user-course");
	var course_id = course.find(".course-id").text();
	
	$.ajax({
		url: "remove/",
		type: "POST",
		data: { 'course_id': course_id },
		success: function(response){
			if(response.success){
				course.fadeOut('slow', function(){
					course.remove();
				});
				
				var tabs = course.parents(".course-term").find(".tabbed-list");
				var tab = get_tab(tabs, response.course.department.toUpperCase());
				tab.find(".tab-content").empty();
			}else{
				alert("There was a problem removing this course.  Refresh the page, and try again.");
			}
		},
		error: function(request, textStatus, errorThrown){
			alert(error_message);
		},
		dataType: "json"
	});
	
	return false;
});
	