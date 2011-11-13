function get_keys(dict){
	keys = []
	for(key in dict){
		keys.push(key)
	}
	
	return keys;
}

$("form.search-users").livequery('submit', function(){
	var form = $(this);
	var results = $(".search-results");
	results.append("<div class='ajax-call-loading'><img src='/site_media/pics/ajax-loader.gif' /></div>");
	
	if(form.find("input[name=search]").val() != ""){
		submitForm({
			url: "search/",
			form: $(this),
			success: function(response){
				results.empty();
			
				var results_list = $("<ul>").appendTo(results);
				results_list.addClass("search-sections");
				
				if(response.users){
					var keys = get_keys(response.users).sort();
					
					for(i in keys){
						var type = keys[i];
						var users = response.users[keys[i]];
						if(users.length > 0){
							var section = $("<li>").append("<h3>" + type + "</h3>");
							section.addClass("search-section");
							section.append(create_user_list_display(users));
							results_list.append(section);
						}
					}
				}else{
					results_list.append("<li class='no-results'>Search found no results.</li>");
				}
			},
			invalid: function(){},
			complete: function(){
				results.find("img").parent().remove();
			},
			error: function(status, error){
				alert("Error: " + status + " " + error);
			}
		});
	}else{
		results.empty();
	}
	
	return false;
});

$(".tab").live('click', function(){
	var tab = $(this);
	var tab_type;
	getTabData({
		tab: tab,
		url: "partial/",
		get_data: function(){
			tab_type = tab.parents(".tabbed-list").siblings(".user-grouper").text();
			var letter = tab.find(".tab-name").text();
			return { type: tab_type, letter: letter }
		},
		get_content: function(response){
			var users = response.users;
			if(users.length == 0){
				return $("<p class='no-users'>There are no " + tab_type.toLowerCase() + " in this category.</p>");
			}else{
				return create_user_list_display(users);
			}
		}
	});
	
	if(sessionStorage){
		var letter = tab.find(".tab-name").text();
		var key = tab.parents("li").find(".user-grouper").text().toLowerCase();
		
		sessionStorage.setItem(key, letter);
	}
	
	return false;
});

$("a.add-user").livequery('click', function(){
	var link = $(this);
	var form = link.parent().find("form.add-user");
	var grouper = link.parent().find(".user-grouper").text();
	var link_text = "Add " + grouper.substr(0, grouper.length - 1);
	
	if(form.is(":visible")){
		form.slideUp('slow');
		link.text(link_text);
	}else{
		form.slideDown('slow');
		link.text("Hide");
	}
	
	return false;
});

$("form.add-user").livequery('submit', function(){
	var form = $(this);
	
	submitForm({
		url: "/siteadmin/users/add/",
		form: form,
		success: function(response){
			var user = response.user;
			
			var users_section = form.parents(".users-section");
			
			var grouper = users_section.find(".user-grouper").text();
			users_section.find("a.add-user").text("Add " + grouper.substr(0, grouper.length - 1));
			
			var tab = get_tab(users_section, user.last_name.substr(0, 1).toUpperCase());
			tab.find(".tab-content").empty();
			tab.click();
			
			form.slideUp('slow', function(){
				var full_name = user.first_name + " " + user.last_name;
				var notification = $("<p class='user-add-success'>'" + full_name + "' was added successfully.</p>");
				notification.hide();
				notification.insertAfter(form);
				notification.fadeIn('slow');
				setTimeout(function(){
					notification.fadeOut(800, function(){
						notification.remove();
					});
				}, 1500);
			});
		},
		invalid: function(response){
			if(response.errors.__all__){
				form.find(".form-error").text(response.errors.__all__);
			}
			
			display_errors(form, response.errors);
		},
		error: function(request, textStatus, errorThrown){
			alert(error_message);
		}
	});
	
	return false;
});

$(".user-element").livequery('mouseenter', function(){
	var user = $(this);
	
	if(user.parents(".search-section").length > 0){ //user was searched
		return;
	}
	
	if(!user.find(".user-menu").is(":visible")){
		var menu = $("<span class='user-menu'></span>");
		$("<a href='' class='delete-user'>delete</a>").appendTo(menu);
		menu.appendTo(user);
	}
});

$(".user-element").livequery('mouseleave', function(){
	var user = $(this);
	user.find(".user-menu").remove();
});

$("a.delete-user").livequery('click', function(){
	var link = $(this);
	var user = link.parents(".user-element");

	if(confirm("This user will be deleted permanently.")){		
		var display = user.find(".user-display");
		var username = get_username_from_display(display);
		
		$.ajax({
			url: "/siteadmin/users/delete/",
			type: "POST",
			data: { 'username': username },
			success: function(response){
				if(response.success){
					user.fadeOut('slow', function(){
						var section = user.parents(".users-section");
						
						var tab = get_tab(section, response.user.last_name.substr(0, 1).toUpperCase());
						tab.find(".tab-content").empty();
						tab.click();
						
						user.remove();
					});
				}else{
					alert("There was a problem deleting this user. Try refreshing the page, and deleting again.");
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
