$(document).ready(function(){
	var assignment_date = new Date($(".add-assignment-date-input").val().replace(/-/g, "/"));
	$(".add-assignment-date-input").datepicker({ defaultDate: assignment_date, minDate: 0 });
});

/*
 * Resource scripts
 *
 */
function switch_inputs(){
	var form = $(".add-resource-form");	
	var type = form.find("select[name='type']").val();
	
	if(type == "f"){
		$(".file-section").show();
		$(".link-section").hide();
	}else{
		$(".link-section").show();
		$(".file-section").hide();
	}
}

var resource_form = $(".add-resource-form");
resource_form.find("select[name='type']").livequery('change ready', switch_inputs);
$(document).ready(switch_inputs);
/* End resource scripts */

$(".leave-comment").livequery('click', function(){
	var comment = $(this).parents(".student").find("textarea");
	
	if($(this).html() == "Comment"){
		comment.slideDown('slow');
		$(this).html("Hide");
	}else{
		comment.slideUp('slow');
		$(this).html("Comment");
	}
	
	return false;
});

$(".view-submission").live('click', function(){
	var link = $(this);
	
	if(link.text() == "View"){
		link.html("Hide");
		link.parents(".submission").find(".submission-view").slideDown('slow');
	}else{
		link.html("View");
		link.parents(".submission").find(".submission-view").slideUp('slow');
	}
	
	return false;
});

$(".grade-submission-form").livequery('submit', function(){
	var form = $(this);
	var submission_id = $(this).parents(".submission").find(".submission-id").text();
	
	var comments_text = form.parents(".submission").find(".submission-comments").text();
	form.append("<input type='hidden' name='comments' value='" + comments_text + "' />");
	
	submitForm({
		url: "submissions/" + submission_id + "/grade/",
		form: form,
		success: function(response){
			var submission = form.parents(".submission");
			
			submission.find(".submission-view").slideUp('slow', function(){
				submission.removeClass("submitted");
				submission.addClass("not-submitted");
				
				submission.css("background-color", "white");
				submission.effect("highlight", { color: "yellow" }, 600);

				submission.find(".score-error").html("");

				submission.find(".view-submission").html("View");
				
				form.find("input[name='score']").val(response.score);
								
				submission.find(".submission-status").text("Graded: ");
				submission.find(".submission-date").text(response.date);
			});
			

		},
		invalid: function(response){
			$.each(response.errors, function(field, error){
				form.find("." + field + "-error").html(error);
			});
		},
		error: function(textStatus, errorThrown){
			alert(error_message);
		}
	});
	
	return false;
});

$(".resource").live('mouseenter', function(){
	var resource_id = $(this).find(".resource-id").text();

	var resource_menu = $("<span>").addClass("resource-menu");
	
	resource_menu.append(" <a class='delete-resource' href=''>delete</a>");
	
	if(!$(this).find(".resource-menu").is(":visible")){
		resource_menu.insertAfter($(this).find(".resource-name"));
	}
});

$(".resource").live('mouseleave', function(){
	$(this).find(".resource-menu").remove();
});

$(".delete-resource").live('click', function(){
	var resource = $(this).parents(".resource");
	var resource_id = resource.find(".resource-id").text();
	
	if(confirm("This resource will be deleted.")){
		$.post("resources/" + resource_id + "/delete/", function(response){
			resource.fadeOut('slow', function(){
				$(this).remove();
			});
		});
	}

	return false;
});

$("a.reset-all").live('click', function(){
	return confirm("This will delete all grades and quiz submissions for this assignment.")
});

$("a.reset-submission").live('click', function(){
	var student = $(this).parents(".student");
	var student_name = student.find(".username-display").text();
	var username = student.find(".username").text();
	
	var confirmed = confirm("This will delete " + student_name + "'s grade and quiz submission for this assignment.")
	if(confirmed){
		var submission_id = student.find(".submission-id").text();
		
		$.ajax({
			type: "post",
			url: "submissions/" + submission_id + "/reset/",
			success: function(response){
				if(response.success){
					student.find("input[type=text]").val("");
					student.find("a:contains('Results')").remove();
				}else{
					alert("There was a problem resetting this submission.  Refresh the page, and try again.");
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
