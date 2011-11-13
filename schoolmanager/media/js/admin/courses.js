function display_courses(courses){
	$("a.add-course").show();

	var column = $(".courses-section");
	column.find(".course-list").remove();
	column.find("p.selection-not-complete").remove();
	
	if(courses.length > 0){
		column.append(create_course_link_list(courses));
	}else{
		column.append("<p class='selection-not-complete'>No courses in this category.</p>");
	}
}

var cache = []
function get_partial_course_list(){
	var term = $(".selected-term").text();
	var department = $(".selected-department").text();

	if(term == ""){
		$(".selection-not-complete").text("You must select a term.");
		return;
	}
	
	if(department == ""){
		$(".department-selection-not-complete").hide();
		return;
	}

	var cache_key = term + department;
	var course_list = cache[cache_key];
	if(course_list == null){
		var courses_section = $(".courses-section");
		courses_section.append("<div class='ajax-call-loading'><img src='/site_media/pics/ajax-loader.gif' /></div>");
		
		$(".selection-not-complete").remove();
		
		$.ajax({
			url: "partial/",
			cache: false,
			data: { 'term': term, 'department': department },
			success: function(response, textStatus, error){			
				course_list = response.courses;
								
				cache[cache_key] = course_list;
				
				display_courses(course_list);
			},
			complete: function(){
				courses_section.find("img").parent().remove();
			}
		});
	}else{
		display_courses(course_list);
	}
}

function add_course_option(term_or_department, id, text){
	$("#id_" + term_or_department).append($("<option>").val(id).text(text));
}

function change_course_option(term_or_department, id, text){
	$("#id_" + term_or_department).find("option[value=" + id + "]").text(text);
}

function remove_course_option(term_or_department, id){
	$("#id_" + term_or_department).find("option[value=" + id + "]").remove();
}

function delete_caches(term_or_department, partial_key){
	var search_category = "term"
	if(term_or_department == "term"){
		search_category = "department"; //we want to go through all of the departments, if the term cache needs to be deleted
	}
	
	$.each($("." + search_category + "-display"), function(i, category_display){
		var cache_key = null;
		if(term_or_department == "term"){
			cache_key = partial_key + $(category_display).text();
		}else{
			cache_key = $(category_display).text() + partial_key;
		}
		
		cache[cache_key] = null;
	});
}

function delete_selected_cache(){
	var term = $(".selected-term").text();
	var department = $(".selected-department").text();
		
	cache[term + department] = null;
}

$(".term-display").livequery('click', function(){
	var term_display = $(this);
	var term_list = term_display.parents(".course-terms");
	
	term_list.find(".selected-term").removeClass("selected-term");
	term_display.addClass("selected-term");

	var departments_section = $(".departments-section");
	departments_section.find(".department-selection-not-complete").remove();
	
	var departments = departments_section.find(".course-departments");
	if(departments.is(":visible")){
		get_partial_course_list();
	}else{
		departments.show();
		$("a.add-department").show();
	}
	
	if(sessionStorage){
		sessionStorage.setItem('term', term_display.text());
	}
	
	return false;
});

$(".department-display").livequery('click', function(){
	var department_display = $(this);
	var department_list = department_display.parents(".course-departments");
	
	department_list.find(".selected-department").removeClass("selected-department");
	department_display.addClass("selected-department");
	
	get_partial_course_list();
	
	if(sessionStorage){
		sessionStorage.setItem('department', department_display.text());
	}
	
	return false;
});

$("a.add-term").live('click', function(){
	var link = $(this);
	var form = link.parents(".terms-section").find("form.add-term");
	var link_text = "Add";
	
	if(link.text() == link_text){
		form.slideDown('slow');
		link.text("Hide");
	}else{
		form.slideUp('slow');
		link.text(link_text);
	}
	
	return false;
});

function make_term_display(term){
	var display = $("<li>");
	display.addClass("term");
	
	display.append("<a href='' class='term-display'>" + term.name + "</a>");
	
	var id_display = $("<span>");
	id_display.addClass("term-id");
	id_display.text(term.id);
	id_display.appendTo(display);
	
	display.append("<span class='term-start'>" + term.start + "</span>");
	display.append("<span class='term-end'>" + term.end + "</span>");
	
	return display;
}

$("form.add-term").livequery('submit', function(){
	var form = $(this);
	
	submitForm({
		url: "/siteadmin/terms/add/",
		form: form,
		success: function(response){
			var term = response.term;
			
			form.slideUp('slow', function(){
				var section = form.parents(".terms-section");
				var term_list = section.find(".course-terms");
				var term_display = make_term_display(term);
				term_display.find("a").hide();
								
				var new_name = term_display.text().substr(0, 2).toLowerCase();
				var new_year = parseInt(term_display.text().substr(2, 4));
								
				var term_list = $(".course-terms");
				
				insert_into_list({
					list: term_list,
					new_ob: term_display,
					comparison: function(new_term, check_term){
						var display_text = check_term.find(".term-display").text();
						
						var check_name = display_text.substr(0, 2);
						var check_year = display_text.substr(2, 4);
						
						if(parseInt(check_year) == new_year){
							if(check_name.toLowerCase() < new_name){
								return true;
							}
						}
						
						return false;
					}
				});
				
				var term_link = term_display.find("a");
				term_link.css("margin-left", "2px");
				term_link.customFadeIn('slow', function(){
					term_link.click();
				});
				
				add_course_option("term", term.id, term.name);
				
				form[0].reset();
				
				section.find("a.add-term").text("Add");
			});
		},
		invalid: function(response){
			if(response.errors.__all__){
				form.find(".form-error").text(response.errors.__all__);
			}
		
			$.each(response.errors, function(field, error){
				form.find("." + field + "-error").text(error);
			});
		},
		error: function(request, textStatus, errorThrown){
			alert("Error adding term");
		}
	});
	
	return false;
});

$("li.term").livequery('mouseenter', function(){
	var term = $(this);
	
	if(!term.find(".term-menu").is(":visible") && !term.find("form.change-term").is(":visible")){
		var menu = $("<span>");
		menu.addClass("term-menu");
		menu.append($("<a href='' class='change-term'>change</a>"));
		menu.append($("<a href='' class='delete-term'>delete</a>"));
		menu.appendTo(term);
	}
});

$("li.term").livequery('mouseleave', function(){
	var term = $(this);
	term.find(".term-menu").remove();
});

$("a.change-term").livequery('click', function(){
	var term = $(this).parents(".term");
	var term_id = term.find(".term-id").text();
	var display = term.find(".term-display");
	
	display.hide();
	
	var change_form = $("form.add-term").clone();
	change_form.removeClass("add-term");
	change_form.addClass("change-term");
	change_form.hide();
	
	var name_input = change_form.find("input[name=name]");
	name_input.val(display.text().substr(0, 2));
			
	change_form.find("input[name=start]").remove();
	change_form.find("input[name=end]").remove();
	
	var start_input = $("<input type='text' name='start' />");
	start_input.val(term.find(".term-start").text());
	start_input.datepicker();
	start_input.insertAfter(change_form.find(".start-error").parent().find("label"));
	
	var end_input = $("<input type='text' name='end' />");
	end_input.val(term.find(".term-end").text());
	end_input.datepicker();
	end_input.insertAfter(change_form.find(".end-error").parent().find("label"));
	
	var submit_input = change_form.find("input[type=submit]");
	submit_input.val("Change");
	submit_input.parent().append("<a href='' class='cancel-change-term'>Cancel</a>");
	
	change_form.appendTo(term);
	
	term.find(".term-menu").remove();
	
	change_form.slideDown('slow');
	
	return false;
});

$("form.change-term").livequery('submit', function(){
	var form = $(this);
	var term_id = form.parents(".term").find(".term-id").text();
	
	submitForm({
		url: "/siteadmin/terms/" + term_id + "/change/",
		form: form,
		success: function(response){
			var term = form.parents(".term");
			var display = term.find(".term-display");
			var start = term.find(".term-start");
			var end = term.find(".term-end");
			
			var name = response.term.name;
			var year = response.term.start.match(/\d{4}/);
			
			display.text(name + year);
			start.text(response.term.start);
			end.text(response.term.end);
			form.slideUp('slow', function(){
				display.customFadeIn('slow');
				form.remove();
			});
			
			change_course_option("term", response.term.id, name + year);
		},
		invalid: function(response){
			if(response.errors.__all__){
				form.find(".form-error").text(response.errors.__all__);
			}
			
			$.each(response.errors, function(field, error){
				form.find("." + field + "-error").text(error);
			});
		},
		error: function(request, textStatus, errorThrown){
			alert(error_message);
		}
	});
	
	return false;
});

$(".cancel-change-term").livequery('click', function(){
	var term = $(this).parents(".term");
	var display = term.find(".term-display");
	var form = term.find("form.change-term");
	form.slideUp('slow', function(){
		form.remove();
		display.show();
	});
	
	return false;
});

$(".delete-term").livequery('click', function(){
	var link = $(this);
	var term = link.parents(".term");
	var term_id = term.find(".term-id").text();
	
	if(confirm("All courses in this term will be deleted as well.")){
		$.ajax({
			url: "/siteadmin/terms/delete/",
			type: "POST",
			data: { 'id': term_id },
			success: function(response){
				if(response.success){
					term.customFadeOut('slow', function(){
						term.remove();
						
						$(".course-list").remove();
					});
					
					remove_course_option("term", term_id);
					
					//delete caches
					delete_caches("term", term.find("a.term-display").text());
				}else{
					alert("There was a problem deleting this term. Try refreshing the page, and deleting again.");
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

$("a.add-department").live('click', function(){
	var link = $(this);
	var link_text = "Add";
	var form = link.parents(".departments-section").find("form.add-department");
	
	if(link.text() == link_text){
		link.text("Hide");
		form.slideDown(function(){
			$(".course-departments").show();
			$(".select-term").remove();
		});
	}else{
		link.text(link_text);
		form.slideUp();
	}
	
	return false;
});

function make_department_display(department){
	var display = $("<li>");
	display.addClass("department");
	
	var link = $("<a>");
	link.addClass("department-display");
	link.attr("href", "");
	link.text(department.name);
	link.appendTo(display);
	
	var id_display = $("<span>");
	id_display.addClass("department-id");
	id_display.text(department.id);
	id_display.appendTo(display);
	
	return display;
}

$("form.add-department").livequery('submit', function(){
	var form = $(this);
	
	submitForm({
		url: "/siteadmin/departments/add/",
		form: form,
		success: function(response){
			var new_display = make_department_display(response.department);
			var new_display_text = new_display.find(".department-display").text().toLowerCase();
			
			new_display.find("a").hide();
			
			var department_list = $(".course-departments");
			
			insert_into_list({
				list: $(".course-departments"),
				new_ob: new_display,
				new_ob_val: new_display_text,
				get_val: function(department){
					return department.find(".department-display").text().toLowerCase();
				}
			});
			
			form.slideUp('slow', function(){
				var department_link = new_display.find("a");
				department_link.css("margin-left", "3px");
				department_link.customFadeIn('slow', function(){
					department_link.click();
				});
				$("a.add-department").text("Add");
				
				form[0].reset();
				
				add_course_option("department", response.department.id, response.department.name);
			});
		},
		invalid: function(response){
			display_errors(form, response.errors);
		},
		error: function(request, textStatus, errorThrown){
			alert(error_message);
		}
	});
	
	return false;
});

$("li.department").livequery('mouseenter', function(){
	var department = $(this);
	
	if(!department.find(".department-menu").is(":visible") && !department.find("form.change-department").is(":visible")){
		var menu = $("<span>");
		menu.addClass("department-menu");
		menu.append("<a href='' class='change-department'>change</a>");
		menu.append($("<a href='' class='delete-department'>delete</a>"));
		menu.appendTo(department);
	}
});

$("li.department").livequery('mouseleave', function(){
	var department = $(this);
	department.find(".department-menu").remove();
});

$("a.change-department").livequery('click', function(){
	var department = $(this).parents(".department");
	var display = department.find(".department-display");
	var department_name = display.text();
	
	var change_form = $("form.add-department").clone();
	change_form.removeClass("add-department");
	change_form.addClass("change-department");
	change_form.hide();
	
	change_form.find("input[name=name]").val(department_name);
	
	var submit_input = change_form.find("input[type=submit]");
	submit_input.val("Change");
	submit_input.parent().append("<a href='' class='cancel-change-department'>Cancel</a>");
	
	display.hide()
	$(".department-menu").remove();
	
	department.prepend(change_form);
	change_form.slideDown('slow');
	
	return false;
});

$("form.change-department").livequery('submit', function(){
	var form = $(this);
	var department = form.parents(".department");
	var department_id = department.find(".department-id").text();
	
	submitForm({
		url: "/siteadmin/departments/" + department_id + "/change/",
		form: form,
		success: function(response){
			var display = department.find(".department-display");
			form.slideUp('slow', function(){
				display.text(response.department.name);
				display.customFadeIn('slow');
				
				change_course_option("department", department_id, response.department.name);
			});
		},
		invalid: function(response){
			display_errors(form, response.errors);
		},
		error: function(response){
			alert(error_message);
		}
	});
	
	return false;
});

$(".cancel-change-department").livequery('click', function(){
	var department = $(this).parents(".department");
	var display = department.find(".department-display");
	var form = department.find("form.change-department");
	
	form.slideUp('slow', function(){
		display.show();
		form.remove();
	});
	
	return false;
});

$(".delete-department").livequery('click', function(){
	var link = $(this);
	var department = link.parents(".department");
	var department_id = department.find(".department-id").text();
	
	if(confirm("All courses in this department will be deleted as well.")){
		$.ajax({
			url: "/siteadmin/departments/delete/",
			type: "POST",
			data: { 'id': department_id },
			success: function(response){
				if(response.success){
					department.customFadeOut('slow', function(){
						department.remove();
						
						remove_course_option("department", department_id);
						
						delete_caches("department", department.find("a.department-display").text());
						
						$(".course-list").remove();
					});
				}else{
					alert("There was a problem deleting this department.  Try refreshing the page, and trying again.");
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

$("a.add-course").livequery('click', function(){
	var link = $(this);
	var link_text = "Add";
	var form = link.parents(".courses-section").find("form.add-course");
	
	if(link.text() == link_text){
		link.text("Hide");
		
		var selected_term = $(".selected-term").text();
		var selected_department = $(".selected-department").text();
		
		var term_field = form.find("select[name=term]");
		var selected_val = find_with_text(term_field.find("option"), selected_term);
		if (selected_val)
			term_field.val(selected_val.val());
		
		var department_field = form.find("select[name=department]");
		selected_val = find_with_text(department_field.find("option"), selected_department);
		if (selected_val)
			department_field.val(selected_val.val());
		
		form.slideDown('slow');
	}else{
		link.text(link_text);
		form.slideUp('slow');
	}
	
	return false;
});

$("form.add-course").livequery('submit', function(){
	var form = $(this);
	
	submitForm({
		url: "/siteadmin/courses/add/",
		form: form,
		success: function(response){
			var new_course = make_course_link(response.course);
			new_course.find("a").hide();
			var new_number = parseInt(response.course.number);
			
			var course_list = $(".course-list");
			if(!course_list.is(":visible")){
				var note_display = form.parents(".courses-section").find(".selection-not-complete");
				course_list = $("<ul class='course-list'></ul>");
				course_list.insertAfter(note_display);
				note_display.hide();
			}
			
			insert_into_list({
				list: $(".course-list"),
				new_ob: new_course,
				new_ob_val: new_number,
				get_val: function(check_course){
					return parseInt(check_course.find(".course-link").text().match(/\d+/));
				}
			});
			
			form.slideUp('slow', function(){
				new_course.find("a").customFadeIn('slow');
				$("a.add-course").text("Add");
			});
			
			form[0].reset();
			
			delete_selected_cache();
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

$("li.course").livequery('mouseenter', function(){
	var course = $(this);
	
	if(!course.find(".course-menu").is(":visible")){
		var menu = $("<span>");
		menu.addClass("course-menu");
		menu.append(" <a href='' class='delete-course'>delete</a>");
		menu.appendTo(course);
	}
});

$("li.course").livequery('mouseleave', function(){
	var link = $(this);
	link.find(".course-menu").remove();
});

$("a.delete-course").livequery('click', function(){
	var link = $(this);
	var course = link.parents(".course");
	
	if(confirm("All of this course's data will be deleted.")){
		$.ajax({
			url: "/siteadmin/courses/delete/",
			type: "POST",
			data: { 'id': course.find(".course-id").text() },
			success: function(response){
				if(response.success){
					course.customFadeOut('slow', function(){
						course.remove();
					});
					
					delete_selected_cache();
				}else{
					alert("There was a problem deleting this course.  Try refreshing the page, and trying again.");
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