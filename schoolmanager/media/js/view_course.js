$("a.go-to-assignments").live('click', function(){
	var link = $(this);
	
	link.parents(".course-menu-item").find(".course-notification-count").hide();
});

$(".add-bulletin-form").livequery('submit', function(){
	var form = $(this);
	
	submitForm({
		url: "bulletins/add/",
		form: form,
		success: function(response){
			form[0].reset();
			form.hide();
			$(document).find(".add-bulletin-stand-in").show();
		
			var bulletin_list = $(document).find(".bulletin-list");
			bulletin_list.find(".no-bulletins").remove();
			var new_bulletin = create_bulletin(response.bulletin);
			new_bulletin.hide();
			bulletin_list.prepend(new_bulletin);
			new_bulletin.customFadeIn(600);
		},
		invalid: function(response){
			form.find(".text-error").text(response.errors.text);
		},
		error: function(textStatus, errorThrown){
			alert(error_message);
		}
	});
	
	return false;
});

$(".add-bulletin-stand-in").live('click', function(){
	$(this).hide();
	var bulletin_form = $(document).find(".add-bulletin-form");
	bulletin_form.show();
	bulletin_form.find(".add-bulletin-title").focus();
});

$("a.hide-add-bulletin").live('click', function(){
	var bulletin_board = $(this).parents(".bulletin-board");
	var form = bulletin_board.find(".add-bulletin-form");
	var stand_in = bulletin_board.find(".add-bulletin-stand-in");
	
	form.hide();
	stand_in.show();
	
	return false;
});

$(".comment-form").livequery('submit', function(){
	var form = $(this);
	
	submitForm({
		url: "bulletins/comments/add/",
		form: form,
		success: function(response){
			form[0].reset();
			var new_comment = create_comment(response.comment);
			new_comment.hide();
			form.parent().siblings(".comment-list").append(new_comment);
			new_comment.customFadeIn();
		},
		invalid: function(response){
			form.find(".comment-text-error").text(response.error);
		},
		error: function(textStatus, errorThrown){
			alert(error_message);
		}
	});
	
	return false;
});

$(".delete-bulletin").live('click', function(){
	var bulletin = $(this).parents(".bulletin");
	var bulletin_id = bulletin.find(".bulletin-id").text();
	
	$.ajax({
		type: "POST",
		url: "bulletins/" + bulletin_id + "/delete/", 
		success: function(response){
			if(response.success){
				bulletin.fadeOut();
			}else{
				alert("There was a problem deleting this bulletin.  Refresh the page, and try again.");
			}
		},
		error: function(request, textStatus, errorThrown){
			alert(error_message);
		},
		dataType: "json"
	});
	
	return false;
});

$(".delete-comment").live('click', function(){
	var comment = $(this).parents(".comment");
	var comment_id = comment.find(".comment-id").text();
	
	delete_comment({
		url: "bulletins/comments/" + comment_id + "/delete/",
		success: function(response){
			comment.fadeOut();
		}
	});
	
	return false;
});
