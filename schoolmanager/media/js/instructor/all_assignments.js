function check_weighting(){
	var global_weights_error = $(document).find(".group-weights-error");
	global_weights_error.html("");

	var total = 0;
	var blank = 0;
	var group_weights = $(document).find(".group-weight");
	
	$.each(group_weights, function(i, weight){
		var weight_string = $(weight).html();
		
		if(weight_string != ""){
			total += parseInt(weight_string);
		}else{
			blank += 1;
		}
	});
	
	if (blank == group_weights.length){
		return;
	}else if(blank > 0 && blank < group_weights.length){
		global_weights_error.text("Some group weights are blank. Please make sure that all groups have a weight. (If you want a group worth nothing, set its weight to zero.)");
	}else if(total != 100){
		global_weights_error.text("Group weights add up to '" + total + "%'. Please make sure that group weights only add up to 100%.");
	}
}

$(document).ready(function(){
	check_weighting();
	
	load_upcoming_data($(".upcoming"));	

	$("#id_name").val("");

	$("a.instruction-question").live("click", function(){
		var text_element = $(this).parent().find(".instruction-text");
		
		if(text_element.is(":visible")){
			text_element.slideUp();
		}else{
			text_element.slideDown();
		}
		
		return false;
	});

	/* Add New Group
	 *
	 */
	$("#add_group_form").submit(function(){
		var form = $(this);
		$("add_group_notification").html("Adding group...");
		submitForm({
			url: "groups/add/",
			form: $("#add_group_form"),
			success: function(data){
				var new_group_name = data.group.name;
					
				var group_weight = "";
				if(data.group.weight != null){
					group_weight = data.group.weight;
				}
				
				if($("#group_list").children(".group").length == 0){
					$("#group_list").empty(); //get rid of "You must add a group..."
				}
				
				//add new group
				new_group = $("<li>").addClass("group");
				
				new_group_header = $("<div class='group-header'>");
				new_group_header.append($("<span>").addClass("group-name").html(new_group_name));
				new_group_header.append($("<span>").addClass("group-id").text(data.group.id));
				if(group_weight != "" || group_weight != null){
					new_group_header.append($("<span>").addClass("group-weight-display").text(" (" + group_weight + "%)"));
				}
				new_group_header.append("<span class='group-weight'>" + group_weight + "</span>");
				new_group_header.append(" <a href='' class='delete-group'>delete</a>");
				
				new_group_assignments = $("<ul>").addClass("assignment-list");
				new_group_assignments.append($("<li>").addClass("no-assignments").html("No assignments..."));
				
				new_group.append(new_group_header);
				new_group.append("<a href='' class='add-assignment'>Add Assignment</a>");
				new_group.append(new_group_assignments);
				
				new_group.hide();
				$("#group_list").append(new_group);
				new_group.customFadeIn('slow');
				
				$("#add_group_form")[0].reset(); //reset form
				
				//clear errors
				form.find("[class$='-error']").text("");
				
				check_weighting();
			},
			invalid: function(response){
				$.each(response.errors, function(field, error){
					$(".group-" + field + "-error").html(error); //add errors to input field error spans
				});
			},
			error: function(textStatus, errorThrown){
				alert(error_message);
			}
		});
		
		return false;
	});
	/* End Add New Group */
	
	
	
	$(".group-header").live('mouseenter', function(e){
		$(this).find(".delete-group").show();
		e.stopPropagation();
	});
	
	$(".group-header").live('mouseleave', function(e){
		$(this).find(".delete-group").hide();
		e.stopPropagation();
	});
	
	$("a.delete-group").live('click', function(){
		var delete_group_link = $(this);
		var group = $(this).parents(".group");
		
		group_id = $(this).siblings(".group-id").text();

		assignment_count = group.find(".assignment-list").children(".assignment").length;
		if(assignment_count === 0){ //if group has no assignments, delete it
			$.post("groups/" + group_id + "/delete/", function(response){
				if(response){
					if(response.success){
						group.fadeOut('slow', function(){
							$(this).remove();
							check_weighting();
						});
					}else{
						alert("An error occured when deleting this group.  Please try again.");
					}
				}else{
					alert(error_message);
				}
			});
		}else{ //display transfer menu
			if(!group.find(".delete-group-menu").is(":visible")){
				var menu = $("<div>").addClass("delete-group-menu");
				menu.hide();
				menu.insertBefore(group.find(".add-assignment"));
				menu.append($("<label>").text("Transfer assignments to "));
				var select = $("<select>").addClass("transfer-id-input");
				select.append("<option value=''>None (Delete Assignments)</option>");
				
				$.each($(this).parents(".group").siblings(), function(i, group){
					var group_name = $(group).find(".group-name").text();
					var group_id = $(group).find(".group-id").text();
					select.append("<option value=" + group_id + ">" + group_name + "</option>");
				});
				
				menu.append(select);
				menu.append("<a href='' class='confirmed-delete-group'>delete</a>");
				menu.append("<a href='' class='hide-delete-group-menu'>cancel</a>");
				menu.slideDown(function(){
					delete_group_link.hide();
				});
			}
		}
		return false;
	});
	
	$("a.confirmed-delete-group").live('click', function(){
		link = $(this);
		group_id = link.parents(".group").find(".group-id").text();
		transfer_id = link.siblings(".transfer-id-input").children(":selected").val();
		
		if(transfer_id == ""){
			delete_assignments = confirm("Delete assignments as well?");
			if(!delete_assignments){
				return false;
			}
		}
		
		$.post("groups/" + group_id + "/delete/", { 'transfer_group': transfer_id }, function(data){
			if(data){
				if(data.success){
					if(transfer_id){ //assignments were transfered to another group						
						transfer_group = find_with_text($(".group-id"), transfer_id).parents(".group");
						
						assignments = link.parents(".group").find(".assignment-list").children().detach();
						
						link.parents(".group").fadeOut('slow', function(){ //remove group
							$(this).remove();
							
							assignments.hide();
							transfer_list = transfer_group.find(".assignment-list");
							transfer_list.children(".no-assignments").remove();
							transfer_list.append(assignments);
							assignments.fadeIn('slow');
							
							check_weighting();
						});
						
					}else{
						link.parents(".group").fadeOut('slow', function(){
							$(this).remove(); //remove group
							check_weighting();
						});
					}
				}else{
					//problem deleting group
				}
			}else{
				alert(error_message);
			}
		});
		
		return false;
	});
	
	$("a.hide-delete-group-menu").live("click", function(){
		$(this).parents(".group").find(".delete-group-menu").slideUp(function(){
			$(this).remove();
		});
	
		return false;
	});
	
	/* End Delete Group */
	
	/* Add New Assignment */
	$("a.add-assignment").live('click', function(){
		var link = $(this);
		var group = link.parents(".group");
		
		if(group.find(".add-assignment-form").is(":visible")){
			var assignment_form = group.find(".add-assignment-form");
			assignment_form.slideUp(600, function(){
				link.text("Add Assignment");
				assignment_form.remove();
				group.find(".average-header").show();
			});
		}else{
			var assignment_form_html = $(".add-assignment-form-section").html();
			var assignment_form = $(assignment_form_html);
			assignment_form.find("input[name=group_id]").val(group.find(".group-id").text());
			assignment_form.find(".add-assignment-date-input").datepicker({ minDate: 0 });
			assignment_form.hide();
			
			assignment_form.insertAfter(link);
			assignment_form.slideDown(600);
			link.text("Hide");
			group.find(".average-header").hide();
		}
		
		return false;
	});
	
	$(".add-assignment-form").livequery('submit', function(){
		var form = $(this);
		var group = form.parents(".group");
				
		submitForm({
			url: "add/",
			form: form,
			success: function(data){			
				var new_assignment_id = "<span class='assignment-id'>" + data.assignment.id + "</span>";
				var new_assignment_link = " <a href='" + data.assignment.id + "/' class='assignment-name'>" + data.assignment.name + "</a>";
				var new_assignment_menu = $("<span>").addClass("assignment-menu");
				var delete_assignment_link = " <a href='' class='delete-assignment'>delete</a>";
				new_assignment_menu.append(delete_assignment_link);
				
				var new_assignment = $("<li>").addClass("assignment");
				new_assignment.append(new_assignment_id);
				new_assignment.append(new_assignment_link);
				new_assignment.append(new_assignment_menu);
							
				form.slideUp('slow', function(){
					group.find(".add-assignment").html("Add Assignment");
					group.find("li.no-assignments").remove();
				
					group.find("ul.assignment-list").append(new_assignment);
					new_assignment.hide();
					new_assignment.customFadeIn('slow');
				});
			},
			invalid: function(response){
				form.find("span[class$='-error']").text("");
				
				$.each(response.errors, function(field, error){
					form.find(".assignment-" + field + "-errors").text(error);
				});
			},
			error: function(textStatus, errorThrown){
				alert(error_message);
			}
		});
		
		return false;
		
	});
	/* End Add Assignment */
	
	/* Transfer Assignment */
	$("select.transfer-select").live(($.browser.msie ? "click" : "change"), function(){
		var assignment = $(this).parents(".assignment");
		
		var transfer_id = $(this).val();
		var assignment_id = $(this).parents(".assignment").find(".assignment-id").text();
		
		$.post(assignment_id + "/transfer/", { 'transfer_id': transfer_id }, function(response){
			if(response.success){
				assignment.customFadeOut('slow', function(){
					var group = find_with_text($(".group-id"), transfer_id).parents(".group");
					group.find(".assignment-list").append(assignment);
					
					group.find(".no-assignments").remove();
										
					assignment.customFadeIn('slow');
					assignment.show();
					
					assignment.find(".transfer-message").remove();
					assignment.find(".transfer-select").remove();
		
					assignment.find("a.delete-assignment").hide();
				});
			}else{
				alert("This assignment could not be transfered.  Refresh the page, and try again.");
			}
		});
	});
	/* End Transfer Assignment */
	
	/* Delete Assignment */
	$("li.assignment").live('mouseenter', function(){
		//transfer selection
		
		$.each($("li.assignment").not($(this)), function(i, assignment){
			$(assignment).find(".transfer-message").remove();
			$(assignment).find(".transfer-select").remove();
			$(assignment).find("a.delete-assignment").hide();
		});
		
		var transfer_message = $("<span class='transfer-message'>transfer to: </span>");
		var select = $("<select>").addClass("transfer-select");
		select.mouseleave(function(event) { event.stopPropagation(); });
		select.append("<option value=''>-----</option>");
		
		$.each($(this).parents(".group").siblings(), function(i, group){
			var group_name = $(group).find(".group-name").text();
			var group_id = $(group).find(".group-id").text();
			select.append("<option value=" + group_id + ">" + group_name + "</option>");
		});
		
		if(!$(this).find("a.delete-assignment").is(":visible")){ //if delete link is hidden
			$(this).find("a.delete-assignment").before(transfer_message);
			$(this).find("a.delete-assignment").before(select);
			$(this).find("a.delete-assignment").show();
		}
	});
	
	$("li.assignment").live('mouseleave', function(){
		$(this).find(".transfer-message").remove();
		$(this).find(".transfer-select").remove();
		
		$(this).find("a.delete-assignment").hide();
	});
	
	$("a.delete-assignment").live('click', function(){
		var assignment_link = $(this);
		var assignment = $(this).parents(".assignment");
		var assignment_name = assignment.find(".assignment-name").text();
		var assignment_id = assignment.find(".assignment-id").text();
	
		if(confirm("All data related to this assignment will be deleted, including grades, submissions, and quizzes.")){
			$.ajax({
				type: "post",
				url: assignment_id + "/delete/",
				success: function(response){
					if(response.success){
						assignment.fadeOut('slow', function(){
							$(this).remove();
						});
					}else{
						alert("There was a problem deleting this assignment.  Refresh the page, and try again.");
					}
				},
				error: function(request, text, code){
					alert(error_message);
				},
				dataType: "json"
			});
		}	
	
		return false;
	});
	/* End Delete Assignment */
	
    $(".add-assignment-form select[name='type']").livequery('change', function(){
        var select_elem = $(this);
        var form = select_elem.parents(".add-assignment-form");
        var input = form.find("input[name='possible_score']");
        
        if(select_elem.val() === "o"){
            input.val("");
            input.parents(".form-field").hide();
        }else{
            input.parents(".form-field").show();
        }
        
    });
	
	/* Group Weighting */
	$(".group-header").livequery('mouseenter', function(e){
		
		if($(this).find(".group-weight-display").is(":visible")){
			$(this).find(".group-weight-display").hide();
		}
		
		var weight = $(this).find(".group-weight").text();
		
		if(!$(this).find(".group-weight-form").is(":visible")){
			var form = $("<form>").addClass("group-weight-form").attr("method", "post").append("(");
			var weight_input = $("<input type='text' value='" + weight + "' name='weight' class='group-weight-input' />");
			//weight_input.bind('mouseenter mouseleave', function(e){ e.stopPropagation() });
			form.append(weight_input);
			//form.append($("<input>").attr("type", "text").attr("value", weight).attr("name", "weight").addClass("group-weight-input"));
			form.append("% ");
			form.append($("<input>").attr("type", "submit").attr("value", "Change"));
			form.append($("<span>").addClass("weight-error"));
			form.append(")");
		
			$(this).find(".group-weight").before(form);
		}
	});
	
	$(".group-header").live('mouseleave', function(e){
		$(this).find(".group-weight-form").remove();
	
		$(this).find(".group-weight-display").show();
	});
	
	$(".group-weight-form").livequery('submit', function(){
		var form = $(this);
		var group = form.parent();
		var group_id = form.siblings(".group-id").text();
		
		submitForm({
			url: "groups/" + group_id + "/change/",
			form: form,
			success: function(response){
				var weight = "";
				if(response.weight != null){
					weight = response.weight;
				}
			
				group.find(".group-weight").text(weight);
				
				if(weight === "" || weight === null){
                    group.find(".group-weight-display").remove();
				}else{
					if(group.children(".group-weight-display").length == 0){
						var display = $("<span>").addClass("group-weight-display");
						display.text("(" + weight + "%)");
						
						group.find(".group-weight").before(display);
					}else{
						group.find(".group-weight-display").text("(" + weight + "%)").show();
					}
				}
				
				group.find(".group-weight-form").remove();
				
				check_weighting();
			},
			invalid: function(response){
				group.find(".weight-error").text("" + response.error);
			},
			error: function(response){
				alert(error_message);
			}
		});
		
		return false;
	});
});