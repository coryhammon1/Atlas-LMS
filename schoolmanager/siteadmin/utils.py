
def get_user_type(user):
	if user.is_superuser:
		return "Administrators"
	elif user.is_staff:
		return "Instructors"
	else:
		return "Students"
