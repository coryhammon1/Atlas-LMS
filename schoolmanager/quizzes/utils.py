
def group_choices_by_question(choices): #choices must be a list
	choices.sort(key=lambda choice: choice.question_id)
	
	questions = []
	current_question_id = None
	current_question_choices = None
	for choice in choices:
		if choice.question_id != current_question_id:
			#add a new question
			current_question_id = choice.question_id
			current_question_choices = []
			
			questions.append({ 'id': choice.question.id, 'text': choice.question.text, 
								'points': choice.question.points, 'choices': current_question_choices })
			
		current_question_choices.append(choice)
		
	return questions