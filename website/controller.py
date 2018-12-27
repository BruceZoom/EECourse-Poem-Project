# coding:utf-8
import web
import sys
import codecs
import utils
import time
import json
import os
from PIL import Image

# import PoemModel as PM

# from model.getImageFeature import *
# from model.modernPoemGenerate import *
# from translate import *

render = web.template.render('templates')

urls = (
    '/', 'index',
    '/index', 'index',
    '/query', 'query',
    '/gallery', 'gallery',
    '/gallery_image', 'gallery_image',
    '/gallery_poem', 'gallery_poem',
    '/analyzed', 'analyzed',
    '/analyzer', 'analyzer'
)

EMPTY_QUERY = 0
VALID_QUERY = 1
VALID_IMAGE = 2
INVALID_QUERY = 3


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
        print (inputs)
        data = {
            'form': utils.FORM_INIT,
            'header': utils.HEADER,
            'pagi': utils.PAGI_SETTING,
        }
        validation = Validator.form_validate(inputs)

        if validation == EMPTY_QUERY:
            data['landing'] = utils.LANDING_DATA_DEFAULT
            return render.index(data=data)

        elif validation == VALID_QUERY:
            # parse form inputs and make query
            command_dict = Validator.to_command_dict(inputs)
            print (command_dict)
            # data['total_match'], data['results'] = PM.common_query(command_dict)
            # print data['total_match'], data['results']
            # data['pagi']['max_page'] = (data['total_match'] + data['pagi']['result_per_page'] - 1) // data['pagi'][
            #     'result_per_page']
            data['results'] = utils.ENTRY_SAMPLES

            # set up other data
            # data['form'] = {key: inputs[key] for key in utils.FORM_INIT.keys()}
            data['form'] = inputs.copy()
            # data['form']['image'] = data['form']['image'].decode()  # 否则会出现byte和str报错
            # print(data['form'])
            data['url_prefix_form'] = '&'.join([key + '=' + value for key, value in data['form'].items()]) + '&'
            # print(data['url_prefix_form'])
            return render.gallery(data=data)

        elif validation == VALID_IMAGE:
            image_inputs = web.input(image={})
            # filename = image_inputs.image.filename.replace('\\', '/').split('/')[-1]
            utils.timestamp += 1

            _basename = os.path.basename(image_inputs.image.filename)
            _exten_name = os.path.splitext(_basename)[1].lower()
            filename = str(utils.timestamp) + _exten_name
            data['upload_prefix'] = utils.UPLOAD_PREFIX
            with codecs.open(utils.UPLOAD_PREFIX + filename, 'wb') as fout:
                fout.write(image_inputs.image.file.read())
            if(_exten_name=='png'):#四通道图像会在vgg步骤报错
                im = Image.open(utils.UPLOAD_PREFIX + filename)
                newim = im.convert(mode='RGB')
                filename = str(utils.timestamp) + '.jpg'
                newim.save(utils.UPLOAD_PREFIX +filename)
                os.remove(utils.UPLOAD_PREFIX + str(utils.timestamp) + _exten_name)

            data['results'] = utils.ENTRY_SAMPLES
            data['form']['image'] = filename
            data['url_prefix_form'] = '&'.join([key + '=' + data['form'][key] for key in data['form'].keys()]) + '&'

            # data['ioscene'] = 'ioscene'
            # data['heatmap'] = filename
            # objects = ['a', 'b', 'c']
            # scene = ['a', 'b', 'c']
            # attributes = ['a', 'b', 'c']
            #
            # objectStr = ', '.join([x[0] for x in objects])
            # sceneStr = ', '.join([x[0] for x in scene])
            # attributesStr = ', '.join(attributes)
            # # 考虑将以上str换为带超链接或者div鼠标悬浮显示的，显示出近义诗、词语（近义列表后面会做）
            # # 另外，最好这个页面是动态加载出来的，防止模型计算过长时间
            # data['object'], data['scene'], data['attributes'] = objectStr, sceneStr, attributesStr

            return render.analyzed(data=data)
        else:
            pass


class gallery:
    def GET(self):
        inputs = web.input()
        print (inputs)
        data = {
            'form': utils.FORM_INIT,
            'header': utils.HEADER,
            'pagi': utils.PAGI_SETTING,
            'results': utils.ENTRY_SAMPLES,
        }
        validation = Validator.form_validate(inputs)
        if validation == VALID_QUERY:
            if 'query' in inputs.keys():
                # data['form'] = {key: inputs[key] for key in utils.FORM_INIT.keys()}
                data['form'] = inputs.copy()
                try:
                    inputs['page'] = int(inputs['page'])
                except Exception as e:
                    print (e.message)
                    inputs['page'] = 1

                command_dict = Validator.to_command_dict(inputs)
                print (command_dict)
                # data['total_match'], data['results'] = PM.common_query(command_dict, cur_page=inputs['page'])
                # print data['total_match'], data['results']
                # data['pagi']['max_page'] = (data['total_match'] + data['pagi']['result_per_page'] - 1) // data['pagi'][
                #     'result_per_page']
                data['results'] = utils.ENTRY_SAMPLES

                data['url_prefix_form'] = '&'.join([key + '=' + data['form'][key] for key in data['form'].keys()]) + '&'
                data['pagi']['cur_page'] = inputs['page']
                return render.gallery(data=data)
        else:
            data = {
                'form': utils.FORM_INIT,
                'header': utils.HEADER,
                'landing': utils.LANDING_DATA_DEFAULT,
            }
            return render.index(data=data)


class gallery_poem:
    def GET(self):
        inputs = web.input()
        print (inputs)
        data = {
            'header': utils.HEADER,
            'image': inputs['image'],
            'relu': inputs['relu'],
        }
        enList = get_poem(inputs['image'], inputs['relu'])[0].split('\n')
        zhList = []
        for sentence in enList:
            zhSentence = en_to_zn_translate(sentence)
            zhList.append(zhSentence)
        enStr = '<br>'.join(enList)
        zhStr = '<br>'.join(zhList)
        data['enStr'] = enStr
        data['zhStr'] = zhStr

        return render.gallery_poem(data=data)


class analyzed:
    def GET(self):
        inputs = web.input()
        return render.index()


class analyzer:
    def POST(self):
        inputs = web.input()
        filename = inputs['filename']
        data = dict()

        # objects, scene, data['ioscene'] = getHybridFeature(filename)
        # attributes, data['heatmap'] = getHeatmap(filename)
        # objects, data['relu'] = getObjectFeature(filename)
        # scene, attributes, data['heatmap'], data['ioscene'] = getSceneFeature(filename)

        data['ioscene'] = 'ioscene'
        data['heatmap'] = utils.UPLOAD_PREFIX + filename
        objects = ['a', 'b', 'c']
        scene = ['a', 'b', 'c']
        attributes = ['a', 'b', 'c']

        objectStr = ' ' + ', '.join([x[0] for x in objects])
        sceneStr = ' ' + ', '.join([x[0] for x in scene])
        attributesStr = ' ' + ', '.join(attributes)
        # objectStr = ', '.join([x[0] for x in objects])
        # sceneStr = ', '.join([x[0] for x in scene])
        # attributesStr = ', '.join(attributes)
        # 考虑将以上str换为带超链接或者div鼠标悬浮显示的，显示出近义诗、词语（近义列表后面会做）
        # 另外，最好这个页面是动态加载出来的，防止模型计算过长时间
        data['object'], data['scene'], data['emotion'] = objectStr, sceneStr, attributesStr
        data['label_complete'] = objects[0][0]
        # print json.dumps(data)
        # return data
        time.sleep(3)
        return json.dumps(data)


class Validator:
    ancient_key_map = {
        'ancientAuthor': 'author',
        'ancientTime': 'dynasty',
        'ancientType': 'label',
        'ancientLabel': 'label',
        'ancientTitle': 'title_tokened',
    }
    modern_key_map = {
        'modernTitle': 'title_tokened',
        'modernAuthor': 'author',
        'modernLabel': 'label',
    }
    common_key_map = {
        'author': 'author',
        'title': 'title_tokened',
        'label': 'label',
        'content': 'content',
    }

    @staticmethod
    def form_validate(form_dict):
        flag = True
        for key in ['query', 'searchType', 'image']:
            flag = (flag and key in form_dict.keys())
        if not flag:
            print ('Failed! Invalid query 1!')
            return INVALID_QUERY
        if len(form_dict['image']) > 0:
            return VALID_IMAGE
        flag = False
        for key in ['query', 'ancientAuthor', 'ancientTime', 'ancientType', 'ancientLabel', 'ancientTitle',
                    'modernTitle', 'modernAuthor', 'modernLabel']:
            flag = (flag or (key in form_dict.keys() and len(form_dict[key]) > 0))
        if not flag:
            print ('Failed! Empty query 1!')
            return EMPTY_QUERY
        if len(form_dict['query']) > 0:
            flag = False
            for key in ['author', 'title', 'label', 'content']:
                flag = (flag or key in form_dict.keys())
            if not flag:
                print ('Failed! Invalid query 2!')
                return INVALID_QUERY
            return VALID_QUERY
        else:
            return VALID_QUERY

    @staticmethod
    def to_command_dict(input_dict):
        command_dict = dict()
        for key in ['author', 'title', 'label', 'content']:
            if key in input_dict.keys():
                command_dict[Validator.common_key_map[key]] = (input_dict['query'], False)
        command_dict['searchType'] = input_dict['searchType']
        if input_dict['searchType'] == 'ancient':
            if 'accurate' in input_dict.keys():
                for key in ['ancientAuthor', 'ancientTime', 'ancientType', 'ancientLabel', 'ancientTitle']:
                    if input_dict[key] != '':
                        command_dict[Validator.ancient_key_map[key]] = (input_dict[key], True)
        elif input_dict['searchType'] in ['modern', 'all']:
            if 'accurate' in input_dict.keys():
                for key in ['modernTitle', 'modernAuthor', 'modernLabel']:
                    if input_dict[key] != '':
                        command_dict[Validator.modern_key_map[key]] = (input_dict[key], True)

        return command_dict


if __name__ == "__main__":
    #sys.argv.append('8000')
    app = web.application(urls, globals())
    app.run()
