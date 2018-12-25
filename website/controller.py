# coding:utf-8
import web
import sys
import cv2
import codecs
from skimage import io
from model.getImageFeature import *
from model.modernPoemGenerate import *
from translate import *
import utils

render = web.template.render('templates')

urls = (
	'/','index',
	'/index', 'index',
	'/query', 'query',
	'/gallery', 'gallery',
	'/gallery_image','gallery_image',
	'/gallery_poem','gallery_poem'
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
			data['form']['image']=data['form']['image'].decode()#否则会出现byte和str报错
			print(data['form'])
			data['url_prefix_form'] = '&'.join([key + '=' + value for key,value in data['form'].items()]) + '&'
			print(data['url_prefix_form'])
			return render.gallery(data=data)
		elif validation == VALID_IMAGE:
			image_inputs = web.input(image={})
			filename = './static/upload/' + image_inputs.image.filename.replace('\\', '/').split('/')[-1]
			with codecs.open(filename, 'wb') as fout:
				fout.write(image_inputs.image.file.read())
			#load_image(filename)
			# # img = io.imread(filename)
			# # io.imshow(img)
			# cv2.imshow('loaded', cv2.imread(filename, cv2.IMREAD_COLOR))
			data['results'] = utils.ENTRY_SAMPLES
			data['form']['image']=filename
			data['url_prefix_form'] = '&'.join([key + '=' + data['form'][key] for key in data['form'].keys()]) + '&'

			objects,data['relu']=getObjectFeature(filename)
			scene,attributes,data['heatmap'],data['ioscene']=getSceneFeature(filename)

			print(data['url_prefix_form'])
			objectStr=', '.join([x[0] for x in objects])
			sceneStr=', '.join([x[0] for x in scene])
			attributesStr=', '.join(attributes)
			#考虑将以上str换为带超链接或者div鼠标悬浮显示的，显示出近义诗、词语（近义列表后面会做）
			#另外，最好这个页面是动态加载出来的，防止模型计算过长时间
			data['object'],data['scene'],data['attributes']=objectStr,sceneStr,attributesStr

			return render.gallery_image(data=data)
		else:
			pass

class gallery_poem:
	def GET(self):
		inputs = web.input()
		print (inputs)
		data = {
			'header': utils.HEADER,
			'image':inputs['image'],
			'relu':inputs['relu'],
		}
		enList=get_poem(inputs['image'],inputs['relu'])[0].split('\n')
		zhList=[]
		for sentence in enList:
			zhSentence=en_to_zn_translate(sentence)
			zhList.append(zhSentence)
		enStr='<br>'.join(enList)
		zhStr='<br>'.join(zhList)
		data['enStr']=enStr
		data['zhStr']=zhStr

		return render.gallery_poem(data=data)


class gallery:
	def GET(self):
		inputs = web.input()
		print (inputs)
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
			except Exception as  e:
				print (e.message)
				inputs['page'] = 1
			data['pagi']['cur_page'] = inputs['page']
			return render.gallery(data=data)
		else:
			return render.gallery(data=data)


class Validator:
	@staticmethod
	def form_validate(form_dict):
		print (len(form_dict['image']))
		if len(form_dict['query']) <= 0 and len(form_dict['image']) <= 0:
			return EMPTY_QUERY
		if len(form_dict['image']) > 0:
			return VALID_IMAGE
		if len(form_dict['query']) > 0:
			return VALID_QUERY


if __name__ == "__main__":
	#sys.argv.append('8000')
	app = web.application(urls, globals())
	app.run()
