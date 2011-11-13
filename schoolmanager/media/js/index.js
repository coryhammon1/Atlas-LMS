function assignment_stream_item(assignment){
	return assignment.text + " on " + assignment.date;
}

function adjust_stream_widths(){
	var wrapper = $(".course-stream-wrapper");
	if(wrapper.length > 0){
		var wrapper_width = wrapper.width();
		$(".course-stream-section").width(Math.ceil(wrapper_width/2)+1);
	}
}

function get_stream_data(section){
	var s = $(section);
	var course_url = s.find(".course-url").text();
	var course_stream = s.find(".course-stream");

	if(s.find(".ajax-call-loading").is(":visible")){
		$.ajax({
			type: "get",
			url: "/courses/" + course_url + "/stream/",
			cache: false,
			success: function(response){
				if(response == null || response.length == 0){
					course_stream.append("<li class='no-stream-data'>No recent activity</li>");
				}else{
					for(i=0; i<response.length; i++){
						if(response[i].type == "assignment"){
							course_stream.append("<li class='stream-item'>" + assignment_stream_item(response[i]) + "</li>");
						}else if (response[i].type == "bulletin"){
							var bulletin = create_bulletin(response[i].bulletin);
							
							var comments = response[i].bulletin.comments;
							var comment_list = bulletin.find(".comment-list");
							
							for(x=0; x<comments.length; x++){
								comment_list.append(create_comment(comments[x]));
							}
							
							course_stream.append(bulletin);
						}
					}
				}
			},
			complete: function(request, textStatus){
				course_stream.find(".ajax-call-loading").remove();
			},
			error: function(XMLHttpRequest, textStatus, errorThrown){
				course_stream.append("<li class='no-stream-data'>Error retrieving activity</li>");
			},
			dataType: "json"
		});
	}
}

$(".comment-form").livequery('submit', function(){
	var form = $(this);
	
	var course_url = form.parents(".course-stream-section").find(".course-url").text()
	
	submitForm({
		url: "/courses/" + course_url  + "/bulletins/comments/add/",
		form: form,
		success: function(response){
			form[0].reset();
			var new_comment = create_comment(response.comment);
			new_comment.hide();
			form.parents(".bulletin").find(".comment-list").append(new_comment);
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
	var course_url = bulletin.parents(".course-stream-section").find(".course-url").text();
	
	$.ajax({
		type: "POST",
		url: "/courses/" + course_url + "/bulletins/" + bulletin_id + "/delete/", 
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
	var course_url = comment.parents(".course-stream-section").find(".course-url").text();
	
	delete_comment({
		url: "/courses/" + course_url + "/bulletins/comments/" + comment_id + "/delete/",
		success: function(response){
			comment.fadeOut();
		}
	});
	
	return false;
});

$(window).load(function(){
	$(".move-stream-left").css("opacity", 0);
	
	var stream_list = $(".course-streams");
	var streams = stream_list.children(".course-stream-section");
	var stream_index = 0;
	
	if(streams.length < 3){
		$(".move-stream-right").css("opacity", 0);
	}

	$(".move-stream-right").click(function(){
		if($(this).css("opacity") == 0){
			return false;
		}
	
		if(stream_index < streams.length - 2){
			stream_index += 1;
		}
		
		get_stream_data(streams[stream_index + 1]);
		
		if(stream_index == streams.length - 2){
			$(this).css("opacity", 0);
		}
		
		$(".move-stream-left").css("opacity", 100);
		
		$(".course-stream-wrapper").animate({
			scrollLeft: '+=' + streams.first().width()
		}, 800);
				
		return false;
	});
	
	$(".move-stream-left").click(function(){
		if(stream_index == 0){
			$(".move-stream-left").css("opacity", 0);
			return false;
		}else if(stream_index > 0){
			stream_index -= 1;
		}
		
		if(stream_index == 0){
			$(".move-stream-left").css("opacity", 0);
		}
		
		$(".move-stream-right").css("opacity", 100);
		
		
		$(".course-stream-wrapper").animate({
			scrollLeft: '-=' + streams.first().width()
		}, 800);
		
		return false;
	});

	var stream_sections = $(".course-stream-section").toArray();
	for(var i in stream_sections){
		if(i > 1) break;
		
		var section = $(stream_sections[i]);
		get_stream_data(section);
	}
});

var link_text;
$(document).ready(function(){
	link_text = $("a.view-future-courses").text();
});

$("a.view-future-courses").click(function(){
	$("ul.future-courses").slideDown();
	
	$(this).removeClass("view-future-courses");
	$(this).addClass("hide-future-courses");
	$(this).text("Hide");
	
	return false;
});

$("a.hide-future-courses").livequery("click", function(){
	$("ul.future-courses").slideUp();
	$(this).removeClass("hide-future-courses");
	$(this).addClass("view-future-courses");
	$(this).text(link_text);
	
	return false;
});