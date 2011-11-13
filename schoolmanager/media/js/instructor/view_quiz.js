function update_total_points(){
	var total_points = 0;
	
	$.each($(".question-points"), function(i, element){
		var points = $(element).text().match(/\d+/);
		total_points += parseInt(points);
	});
	
	$(".total-points").text(total_points + " pts.");
}

function get_question_type_display(type){
	if(type == 'm'){
		return "Check <b>one</b> correct answer.";
	}else if(type == 's'){
		return "Check <b>any combination</b> of correct answers.";
	}
}

function make_question(question){
	var new_question = $("<li>").addClass("question");
	new_question.append("<span class='question-id'>" + question.id + "</span>");

	var question_display = $("<div>").addClass("question-display");
	question_display.append("<span class='question-text'>" + question.text + "</span>");
	question_display.append(" <span class='question-points'>(" + question.points + " pts.)</span>");
	new_question.append(question_display);
	
	new_question.append("<span class='question-type'>" + question.type + "</span>");
	
	var question_type_display = $("<p>").addClass("question-type-display");
	var question_display = get_question_type_display(question.type);
	question_type_display.append(question_display);
	new_question.append(question_type_display);
	
	var answer_form = $("<form>").addClass("choices");
	answer_form.append($(".blank_choice_formset").html());
	new_question.append(answer_form);
	
	return new_question;
}

function make_question_form(text, type, points){
	var form = $("<form>").addClass("update-question");
	
	var type_section = $("<div>").addClass("form-field");
	type_section.append($("<label>").text("Type"));
	var select = $("<select>").attr("name", "type");
	if(type == 'm'){
		select.append("<option value='m' selected='selected'>Multiple Choice</option>");
		select.append("<option value='s'>Select All</option>");
	}else{
		select.append("<option value='m'>Multiple Choice</option>");
		select.append("<option value='s' selected='selected'>Select All</option>");
	}
	
	type_section.append(select);
	type_section.append($("<span>").addClass("type_error"));
	
	
	var text_section = $("<div>").addClass("form-field").addClass("text-field");
	text_section.append($("<label>").text("Question"));
	text_section.append($("<textarea>").attr("name", "text").text(text));
	text_section.append($("<span>").addClass("text_error"));
	
	var points_section = $("<div>").addClass("form-field");
	points_section.append($("<label>").text("Points"));
	points_section.append("<input type='text' name='points' value='" + points + "' />");
	points_section.append($("<span>").addClass("points_error"));
	
	var submit_section = $("<div>").addClass("form-field");
	submit_section.append("<input type='submit' value='Update Question' />");
	
	form.append(type_section).append(text_section).append(points_section).append(submit_section);
	
	return form;
}

$("form.add-question").livequery('submit', function(){
	var form = $(this);
	
	submitForm({
		url: "questions/add/",
		form: $(this),
		success: function(response){
			form[0].reset();
			$(".no-questions").remove();
	
			var new_question = make_question(response.question);
			new_question.hide();
			
			$(".questions").append(new_question);
						
			new_question.customFadeIn('slow');
			
			update_total_points();
		},
		invalid: function(response){
			$.each(response.errors, function(field, error){
				$(document).find("." + field + "_error").html(error);
			});
		},
		error: function(request, textStatus, errorThrown){
			alert(error_message);
		}
	});
	
	return false;
});

$(".edit-question").live('click', function(){
	var link = $(this);
	var question = link.parents(".question");
	
	var form = question.find("form.update-question");
	var display = question.find(".question-display").hide();
	var text = display.find(".question-text");
	
	if(form.length == 0){
		var type = question.find(".question-type").text();
		var points = question.find(".question-points").text();
		make_question_form(text.text(), type, points.match(/\d+/)).insertAfter(display);
		link.text("Hide");
	}else{
		form.remove();
		display.show();
		link.text("Edit");
	}
	
	return false;
});

$("form.update-question").livequery('submit', function(){
	var form = $(this);
	var question = form.parents(".question");
	var question_id = question.find(".question-id").text();
	
	submitForm({
		url: "questions/" + question_id + "/update/",
		form: form,
		success: function(response){
			form.remove();
			var text = question.find(".question-text");
			text.text(response.question.text);
			
			question.find(".question-type").text(response.question.type);
			question.find(".question-points").text("(" + response.question.points + " pts.)");
			
			question.find(".question-display").customFadeIn(800);
			
			var type_display = question.find(".question-type-display");
			type_display.html(get_question_type_display(response.question.type));
			
			update_total_points();
			
			question.find("a.edit-question").text("Edit");
		},
		invalid: function(response){
			$.each(response.errors, function(field, error){
				form.find("." + field + "_error").text(error);
			});
		},
		error: function(request, textStatus, errorThrown){
			alert(error_message);
		}
	});
	
	return false;
});

$(".delete-question").live('click', function(){
	var link = $(this);
	var question = link.parents(".question");
	
	var confirmed = confirm("Question and answers will be deleted.");
	if(confirmed){
		var question_id = question.find(".question-id").text();
		
		$.ajax({
			url: "questions/" + question_id + "/delete/",
			type: "POST",
			success: function(response){
				if(response.success){
					question.fadeOut('slow', function(){
						$(this).remove();
						update_total_points();
					});
				}else{
					alert("There was a problem deleting this question.  Refresh the page, and try again.");
				}
			},
			error: function(){
				alert(error_message);
			},
			dataType: "json"
		});
	}
	
	return false;
});

$(".question").live('mouseenter', function(){
	var question = $(this);
	if(question.find(".question-menu").length == 0){
		var question_menu = $("<span>").addClass("question-menu");
		if(question.find(".update-question").length == 0){
			question_menu.append("<a class='edit-question' href=''>Edit</a>");
		}else{
			question_menu.append("<a class='edit-question' href=''>Hide</a>");
		}
		question_menu.append("<a class='delete-question' href=''>Delete</a>");
		question.prepend(question_menu);
	}
});

$(".question").live('mouseleave', function(){
	$(this).find(".question-menu").remove();
});

$("form.choices").livequery('submit', function(){
	var form = $(this);
	var question = form.parents(".question");
	var question_id = question.find(".question-id").text();
	
	submitForm({
		url: "questions/" + question_id + "/choices/update/",
		form: form,
		success: function(response){
			form.html(response.rendered_form);
			
			form.effect("highlight", { color: "yellow" }, 600);
		},
		invalid: function(response){
			question.find(".error").remove();
		
			$.each(response.errorlist, function(i, errors){
				$.each(errors, function(field, error){
					var field_name_end = i + "-" + field;
					
					var field = question.find("textarea[name$='" + field_name_end + "']");
					var error_element = $("<span>").addClass("error").text(error);
					field.before("<span class='error'>" + error + "</span>");
				});
			});
		},
		error: function(request, textStatus, errorThrown){
			alert(error_message);
		}
	});
	
	return false;
});

$(".delete-choice").live('click', function(){
	var link = $(this);
	var choice_fields = $(this).parents(".choice");
	
	var delete_field = choice_fields.find("input[name$='DELETE']");
	delete_field.attr("checked", true);

	choice_fields.children().hide();
	choice_fields.append("<td>Choice will be deleted upon saving.</td><td></td><td><a href='' class='undelete-choice'>undo</a></td>");

	return false;
});

$(".undelete-choice").live('click', function(){
	var link = $(this);
	var choice_fields = $(this).parents(".choice");
	
	var delete_field = choice_fields.find("input[name$='DELETE']");
	delete_field.attr("checked", false);
	
	choice_fields.children(":visible").remove();
	choice_fields.children(":hidden").show();
	
	return false;
});

$(".add-answer-field").live('click', function(){
	var link = $(this);
	var question = link.parents(".question");
	var question_id = question.find(".question-id").text();
	var total_form_field = question.find("input[name$='TOTAL_FORMS']");
	var total_forms = total_form_field.val();
	
	var visible_fields = $("<tr>").addClass("choice");
	
	var text_cell = $("<td>").addClass("text");
	$("<textarea>").attr("name", "choices-" + total_forms + "-text").appendTo(text_cell);
		
	var correct_cell = $("<td>").addClass("is_correct");
	$("<input>").attr("name", "choices-" + total_forms + "-is_correct").attr("type", "checkbox").appendTo(correct_cell);
	
	var delete_cell = $("<td>").addClass("delete");
	$("<input>").attr("name", "choices-" + total_forms + "-DELETE").attr("type", "checkbox").appendTo(delete_cell);
	$("<a>").addClass("delete-choice").attr("href", "").text("delete").appendTo(delete_cell);
	
	visible_fields.append(text_cell).append(correct_cell).append(delete_cell);
	
	var hidden_fields = $("<tr>");
	
	var choice_id_cell = $("<td>");
	$("<input>").attr("type", "hidden").attr("name", "choices-" + total_forms + "-id").appendTo(choice_id_cell);
	
	var question_cell = $("<td>");
	$("<input>").attr("type", "hidden").attr("name", "choices-" + total_forms + "-question").val(question_id).appendTo(question_cell);
	
	hidden_fields.append(choice_id_cell).append(question_cell);
	
	question.find("table").append(visible_fields).append(hidden_fields);

	total_form_field.val(parseInt(total_forms) + 1);
	
	return false;
});

$(document).ready(function(){
	update_total_points();
});