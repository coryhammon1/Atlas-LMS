from schoolmanager.bulletins.models import Bulletin, BulletinComment

def compile_bulletin_board(board):
	bulletin_list = [] #all bulletins for bulletin board
		
	bulletins = bulletin_board.bulletins.all().order_by("-date")
	for bulletin in bulletins:
		comment_list = [] #all comemnts for bulletin
			
		comments = bulletin.comments.all().order_by("-date")
		for comment in comments:
			comment_data = {'user': comment.user.get_full_name(), 
									  'text': comment.text, 
									  'date': comment.date.isoformat()}
			comment_list.append(comment_data) #combine single comment data
				
		bulletin_data = {'user': bulletin.user.get_full_name(),
								'title': bulletin.title,
								'text': bulletin.text,
								'date': bulletin.date.isoformat(),
								'comments': comment_list}
		bulletin_list.append(bulletin_data)
		
	 return {'pk': bulletin_board.pk, 'bulletins': bulletin_list}