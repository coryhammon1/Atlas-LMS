import os
import datetime

from django.conf import settings

class FileIterWrapper(object):
	def __init__(self, flo, chunk_size = 1024**2):
		self.flo = flo
		self.chunk_size = chunk_size

	def next(self):
		data = self.flo.read(self.chunk_size)
		if data:
			return data
		else:
			self.flo.close()
			raise StopIteration

	def __iter__(self):
		return self


def save_file_to_upload_dir(file, sub_dir=""):
	file_path = settings.UPLOAD_DIR + sub_dir
		
	file_name = file.__unicode__()
	
	if not os.path.exists(file_path):
		os.makedirs(file_path)
			
	with open(file_path + file_name, "wb+") as destination:
		for chunk in file.chunks():
			destination.write(chunk)
	
	return file_path + file_name

def get_uploaded_file(relative_path):
	file_path = settings.UPLOAD_DIR + relative_path
	return FileIterWrapper(open(file_path))

def file_is_safe(file):
	file_extension = os.path.splitext(file.__unicode__())[1]
	
	if file_extension in settings.UNSAFE_FILE_EXTENSIONS:
		return False
	else:
		return True
	

def get_end_of_week(t):
	days_to_weekend = 6 - t.weekday()
	end = t + datetime.timedelta(days=days_to_weekend)
	
	return end.replace(hour=23, minute=59)
	
def get_end_of_next_week(t):
	next_week = t + datetime.timedelta(weeks=1)
	return get_end_of_week(next_week)
		
def get_end_of_next_three_weeks(t):
	week = t + datetime.timedelta(weeks=3)
	return get_end_of_week(week)
	
def save_files_for_submission(files, submission):
	upload_dir = "%s%s/" % (settings.UPLOAD_DIR, submission.user.username)
	submission_errors = {}
	
	for name, file in files:
		file_name = file.__unicode__()

		if file.size > settings.MAX_UPLOAD_FILE_SIZE:
			submission_errors.update({ file_name: "File is too big." })
			continue
	
		if not file_is_safe(file):
			file_extension = os.path.splitext(file_name)[1]
			submission_errors.update({ file_name: "'%s' file type not supported." % file_extension })
			continue

		relative_path = "%s/%d/" % (submission.user.username, submission.assignment.id)
		full_file_path = save_file_to_upload_dir(file, relative_path)
	
		relative_file_path = relative_path + file_name
	
		try:
			submission.files.create(file=relative_file_path, content_type=file.content_type)
		except IntegrityError:
			pass
			
	return submission_errors
	