function user_is_in_list(user, list){
	var user_text = user_text_display(user);
	for(var i in list){
		var other_text = $(list[i]).text();

		if(other_text == user_text){
			return true;
		}
	}
	
	return false;
}

$(".course-add-instructor").live('click', function(){
	var link = $(this);
	var list = $(".tabbed-instructor-list");
	
	if(link.text() == "Add Instructor"){
		list.slideDown('slow');
		link.text("Hide");
	}else{
		list.slideUp('slow');
		link.text("Add Instructor");
	}
	
	return false;
});

$(".tabbed-instructor-list .tab").live('click', function(){
	var tab = $(this);
	getTabData({
		tab: tab,
		url: "../../users/partial/",
		get_data: function(){
			var tab_type = "Instructors";
			var letter = tab.find(".tab-name").text();
			return { type: tab_type, letter: letter };
		},
		get_content: function(response){
			var users = response.users;
			
			var filtered_users = [];
			var instructor_list = $(".admin-instructor-list").find(".user-full-display").toArray();
			for(var i in users){
				var user = users[i];
				
				if(!user_is_in_list(user, instructor_list)){
					filtered_users.push(user);
				}
			}
			
			if(filtered_users.length == 0){
				return $("<p class='no-users'>There are no instructors in this category.</p>");
			}else{
				return create_user_list_display(filtered_users);
			}
		}
	});
	
	return false;
});

$(".course-add-student").live('click', function(){
	var link = $(this);
	var list = $(".tabbed-student-list");
	var link_text = "Add Student";
	
	if(link.text() == link_text){
		list.slideDown('slow');
		link.text("Hide");
	}else{
		list.slideUp('slow');
		link.text(link_text);
	}
	
	return false;
});

$(".tabbed-student-list .tab").livequery('click', function(){
	var tab = $(this);
	getTabData({
		tab: tab,
		url: "../../users/partial/",
		get_data: function(){
			var tab_type = "Students";
			var letter = tab.find(".tab-name").text();
			return { type: tab_type, letter: letter };
		},
		get_content: function(response){
			var users = response.users;
			
			var filtered_users = [];
			var student_list = $(".admin-student-list").find(".user-full-display").toArray();
			for(var i in users){
				var user = users[i];
				
				if(!user_is_in_list(user, student_list)){
					filtered_users.push(user);
				}
			}
			
			if(filtered_users.length == 0){
				return $("<p class='no-users'>There are no students in this category.</p>");
			}else{
				return create_user_list_display(filtered_users);
			}
		}
	});
	
	return false;
});

$(".user-display").livequery('click', function(){
	var display = $(this);
	var display_text = display.text();
	var username = get_username_from_display(display);
		
	var tab_list = display.parents(".tabbed-list");
	
	var user_list;
	if(tab_list.hasClass("tabbed-instructor-list")){ //add to instructor list
		user_list = $(".admin-instructor-list");
	}else{		//add to student list
		user_list = $(".admin-student-list");
	}
	
	var course_id = $(".course-id").text();
	
	$.ajax({
		url: "/siteadmin/courses/" + course_id + "/add_user/",
		data: { 'username': username },
		type: "POST",
		success: function(response){
			if(response.success){
				var new_display = $("<li>");
				new_display.addClass("course-user");
								
				var user_full_display = $("<span>");
				user_full_display.addClass("user-full-display");
				user_full_display.text(user_text_display(response.user));
				user_full_display.appendTo(new_display);
				
				var new_display_text = response.user.last_name + response.user.first_name + response.user.username;
				new_display_text = new_display_text.toLowerCase();
				
				new_display.find("span").hide();
				
				user_list.find(".empty-list").remove();
				
				insert_into_list({
					list: user_list,
					new_ob: new_display,
					new_ob_val: new_display_text,
					get_val: function(user_display){
						return user_display_text_concat(user_display).toLowerCase();
					}
				});
				
				display.parents(".user-element").customFadeOut('slow', function(){
					new_display.find("span").customFadeIn('slow');
				});
				
				var tab = get_tab(display.parents(".tabbed-list"), response.user.last_name.substr(0, 1).toUpperCase());
				tab.find(".tab-content").empty();
			}else{
				alert("Could not add this user to course.  Try refreshing the page, and adding again.");
			}
		},
		error: function(request, textStatus, errorThrown){
			alert(error_message);
		},
		dataType: "json"
	});
	
	return false;
});

$(".course-user").livequery('mouseenter', function(){
	var user = $(this);
	
	if(!user.find(".user-menu").is(":visible")){
		var menu = $("<span>");
		menu.addClass("user-menu");
		menu.append("<a href='' class='remove-user'>remove</a>");
		menu.appendTo(user);
	}
});

$(".course-user").livequery('mouseleave', function(){
	$(this).find(".user-menu").remove();
});

$(".remove-user").livequery('click', function(){
	var user = $(this).parents(".course-user");
	var display = user.find(".user-full-display");
	var username = get_username_from_display(display);
	
	if(confirm("'" + username + "' will be removed from this course.")){
		$.ajax({
			url: "/siteadmin/courses/" + $(".course-id").text() + "/remove_user/",
			type: "POST",
			data: { 'username': username },
			success: function(response){
				if(response.success){
					user.fadeOut('slow', function(){
						var section = user.parents(".course-users-section");
						var tab = get_tab(section, response.user.last_name.substr(0, 1).toUpperCase());
						tab.find(".tab-content").empty();
					
						user.remove();
					});
				}else{
					alert("There was a problem remove this user.  Try refreshing the page, and removing again.");
				}
			},
			error: function(request, textStatus, errorThrown){
				alert(error_message);
			},
			dataType: "json"
		});
	}
	
	return false;
});