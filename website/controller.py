import web
import sys
import cv2
import codecs
from skimage import io
from model.test_model import *

render = web.template.render('templates')

urls = (
	'/', 'index',
	'/query', 'query',
)

DISPLAY_UTILS = {

}

FORM_INIT = {
	'searchType': 'all',
	'query': '',
}

EMPTY_QUERY = 0
VALID_QUERY = 1
VALID_IMAGE = 2

class index:
	def GET(self):
		data = {
			'form': FORM_INIT,
		}
		return render.index(data=data)


class query:
	def POST(self):
		inputs = web.input()
		print inputs
		validation = Validator.form_validate(inputs)
		if validation == EMPTY_QUERY:
			return render.index(data=data)
		elif validation == VALID_QUERY:
			data = {
				'form': {key: inputs[key] for key in FORM_INIT},
			}
			return render.gallery(data=data)
		elif validation == VALID_IMAGE:
			data = {
				'form': FORM_INIT,
			}
			image_inputs = web.input(image={})
			filename = 'tmp/' + image_inputs.image.filename.replace('\\', '/').split('/')[-1]
			with codecs.open(filename, 'wb') as fout:
				fout.write(image_inputs.image.file.read())
			load_image(filename)
			# # img = io.imread(filename)
			# # io.imshow(img)
			# cv2.imshow('loaded', cv2.imread(filename, cv2.IMREAD_COLOR))
			return render.gallery(data=data)
		else:
			pass


class Validator:
	@staticmethod
	def form_validate(form_dict):
		print len(form_dict['image'])
		if len(form_dict['query']) <= 0 and len(form_dict['image']) <= 0:
			return EMPTY_QUERY
		if len(form_dict['image']) > 0:
			return VALID_IMAGE
		if len(form_dict['query']) > 0:
			return VALID_QUERY


if __name__ == "__main__":
	sys.argv.append('8000')
	app = web.application(urls, globals())
	app.run()
