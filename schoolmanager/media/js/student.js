/* Delete Uploaded File */
$(".uploaded-file").live('mouseenter', function(){
	$(this).find(".delete-file").show();
});

$(".uploaded-file").live('mouseleave', function(){
	$(this).find(".delete-file").hide();
});

$(".delete-file").live('click', function(){
	file = $(this).parent();
	file_name = $(this).siblings(".file-name").text();
	file_id = $(this).siblings(".file-id").text();
	
	confirmed = confirm("'" + file_name + "' will be deleted permanently.");
	
	if(confirmed){
		$.ajax({
			url: "../files/" + file_id + "/delete/",
			type: "POST",
			success: function(response){
				if(response.success){
					file.fadeOut('slow', function(){
						$(this).remove();
					});
				}else{
					alert("There was a problem deleting this file.  Refresh this page, and try again.");
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
/* End Delete Uploaded File */

var file_form_count = 1;
$(".add-upload-file").live('click', function(){
	file_uploads = $(this).parent().parent();
	
	add_another_link = $(this).detach();
	
	new_input = $("<input type='file' name='file-" + file_form_count+1 + "' />");
	file_uploads.append($("<li>").addClass("file-upload").append(new_input).append(add_another_link));
	
	file_form_count += 1;
	
	return false;
});