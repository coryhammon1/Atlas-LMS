from schoolmanager.assignments.models import AssignmentSubmission

def get_groups_with_null_scores(course):
	blank_submissions = AssignmentSubmission.objects.select_related("assignment", "assignment__group").filter(assignment__course=course, score__isnull=True)
	null_scored_groups = {}
	for submission in blank_submissions:
		group_name = submission.assignment.group.name
		assignment_name = submission.assignment.name
		
		try:
			assignments = null_scored_groups[group_name]
			
			if not assignment_name in assignments:
				assignments.append(assignment_name)
				
		except KeyError:
			null_scored_groups[group_name] = [assignment_name,]
			
	return null_scored_groups
	
