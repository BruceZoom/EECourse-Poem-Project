# coding:utf-8
import web
import sys
import cv2
import codecs
from skimage import io
from model.test_model import *
import utils

render = web.template.render('templates')

urls = (
	'/index', 'index',
	'/query', 'query',
	'/gallery', 'gallery',
)

EMPTY_QUERY = 0
VALID_QUERY = 1
VALID_IMAGE = 2

class index:
	def GET(self):
		data = {
			'form': utils.FORM_INIT,
			'header': utils.HEADER,
			'landing': utils.LANDING_DATA_DEFAULT,
		}
		return render.index(data=data)


class query:
	def POST(self):
		inputs = web.input()
		print inputs
		data = {
			'form': utils.FORM_INIT,
			'header': utils.HEADER,
			'pagi': utils.PAGI_INIT,
		}
		validation = Validator.form_validate(inputs)
		if validation == EMPTY_QUERY:
			data['landing'] = utils.LANDING_DATA_DEFAULT
			return render.index(data=data)
		elif validation == VALID_QUERY:
			data['results'] = utils.ENTRY_SAMPLES
			data['form'] = {key: inputs[key] for key in utils.FORM_INIT.keys()}
			data['url_prefix_form'] = '&'.join([key + '=' + data['form'][key] for key in data['form'].keys()]) + '&'
			return render.gallery(data=data)
		elif validation == VALID_IMAGE:
			image_inputs = web.input(image={})
			filename = 'tmp/' + image_inputs.image.filename.replace('\\', '/').split('/')[-1]
			with codecs.open(filename, 'wb') as fout:
				fout.write(image_inputs.image.file.read())
			# load_image(filename)
			# # img = io.imread(filename)
			# # io.imshow(img)
			# cv2.imshow('loaded', cv2.imread(filename, cv2.IMREAD_COLOR))
			data['results'] = utils.ENTRY_SAMPLES
			data['url_prefix_form'] = '&'.join([key + '=' + data['form'][key] for key in data['form'].keys()]) + '&'
			return render.gallery(data=data)
		else:
			pass


class gallery:
	def GET(self):
		inputs = web.input()
		print inputs
		data = {
			'form': utils.FORM_INIT,
			'header': utils.HEADER,
			'pagi': utils.PAGI_INIT,
			'results': utils.ENTRY_SAMPLES,
		}
		data['url_prefix_form'] = '&'.join([key + '=' + data['form'][key] for key in data['form'].keys()]) + '&'
		if 'query' in inputs.keys():
			data['form'] = {key: inputs[key] for key in utils.FORM_INIT.keys()}
			data['url_prefix_form'] = '&'.join([key+'='+data['form'][key] for key in data['form'].keys()])+'&'
			try:
				inputs['page'] = int(inputs['page'])
			except Exception, e:
				print e.message
				inputs['page'] = 1
			data['pagi']['cur_page'] = inputs['page']
			return render.gallery(data=data)
		else:
			return render.gallery(data=data)


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
