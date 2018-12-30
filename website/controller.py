# coding:utf-8
import web
import sys
import codecs
import myutils
import time
import json
import os
from PIL import Image

# import PoemModel as PM

from model.getImageFeature import *
from model.modernPoemGenerate import *
from model.gushiwenGenerate import *
from model.association import *
from translate import *

import PoemSearchES as PSES

render = web.template.render('templates')

urls = (
    '/', 'index',
    '/index', 'index',
    '/query', 'query',
    '/gallery', 'gallery',
    '/gallery_image', 'gallery_image',
    '/gallery_poem', 'gallery_poem',
    '/analyzed', 'analyzed',
    '/analyzer', 'analyzer',
    '/matchimage', 'matchimage',
    '/authorpage', 'authorpage',
    '/authorlist', 'authorlist',
    '/poempage', 'poempage',
)

EMPTY_QUERY = 0
VALID_QUERY = 1
VALID_IMAGE = 2
INVALID_QUERY = 3


class index:
    def GET(self):
        data = {
            'form': myutils.FORM_INIT,
            'header': myutils.HEADER,
            'landing': myutils.LANDING_DATA_DEFAULT,
            'footer': myutils.FOOTER,
        }
        return render.index(data=data)


def notfound(form_dict):
    data = {
        'form': myutils.FORM_INIT.copy(),
        'header': myutils.HEADER,
        'footer': myutils.FOOTER,
    }
    for key in data['form'].keys():
        if key in form_dict.keys():
            data['form'][key] = form_dict[key]
    return render.notfound(data=data)


class query:
    def POST(self):
        inputs = web.input()
        print (inputs)
        data = {
            'form': myutils.FORM_INIT,
            'header': myutils.HEADER,
            'pagi': myutils.PAGI_SETTING,
            'footer': myutils.FOOTER,
        }
        validation = Validator.form_validate(inputs)

        if validation == EMPTY_QUERY:
            data['landing'] = myutils.LANDING_DATA_DEFAULT
            return render.index(data=data)

        elif validation == VALID_QUERY:
            # parse form inputs and make query
            data['form'] = inputs.copy()
            command_dict = Validator.to_command_dict(inputs)
            print (command_dict)
            data['total_match'], data['results'] = PSES.common_query(command_dict)
            print (data['total_match'])
            # set up pagination and form
            data['pagi']['max_page'] = (data['total_match'] + data['pagi']['result_per_page'] - 1) // data['pagi'][
                'result_per_page']
            data['pagi']['cur_page'] = 1
            data['form']['image'] = ''
            data['url_prefix_form'] = '&'.join([key + '=' + value for key, value in data['form'].items()]) + '&'

            return render.gallery(data=data)

        elif validation == VALID_IMAGE:
            image_inputs = web.input(image={})
            # filename = image_inputs.image.filename.replace('\\', '/').split('/')[-1]
            myutils.timestamp += 1

            _basename = os.path.basename(image_inputs.image.filename)
            _exten_name = os.path.splitext(_basename)[1].lower()
            filename = str(myutils.timestamp) + _exten_name
            data['upload_prefix'] = myutils.UPLOAD_PREFIX
            with codecs.open(myutils.UPLOAD_PREFIX + filename, 'wb') as fout:
                fout.write(image_inputs.image.file.read())
            if(_exten_name=='png'):#四通道图像会在vgg步骤报错
                im = Image.open(myutils.UPLOAD_PREFIX + filename)
                newim = im.convert(mode='RGB')
                filename = str(myutils.timestamp) + '.jpg'
                newim.save(myutils.UPLOAD_PREFIX +filename)
                os.remove(myutils.UPLOAD_PREFIX + str(myutils.timestamp) + _exten_name)

            data['results'] = myutils.ENTRY_SAMPLES
            data['form']['image'] = filename
            data['url_prefix_form'] = '&'.join([key + '=' + data['form'][key] for key in data['form'].keys()]) + '&'

            return render.analyzed(data=data)
        elif validation == INVALID_QUERY:
            return notfound(inputs)


class gallery:
    def GET(self):
        inputs = web.input()
        print (inputs)
        data = {
            'form': myutils.FORM_INIT,
            'header': myutils.HEADER,
            'pagi': myutils.PAGI_SETTING,
            'results': myutils.ENTRY_SAMPLES,
            'footer': myutils.FOOTER,
        }
        validation = Validator.form_validate(inputs)
        if validation == VALID_QUERY:
            if 'query' in inputs.keys():
                # data['form'] = {key: inputs[key] for key in myutils.FORM_INIT.keys()}
                # print(inputs)
                data['form'] = inputs.copy()
                try:
                    inputs['page'] = int(inputs['page'])
                except Exception as e:
                    print(e)
                    inputs['page'] = 1

                command_dict = Validator.to_command_dict(inputs)
                print (command_dict)
                data['total_match'], data['results'] = PSES.common_query(command_dict, cur_page=inputs['page'])
                # print (data['total_match'], data['results'])
                data['pagi']['max_page'] = (data['total_match'] + data['pagi']['result_per_page'] - 1) // data['pagi'][
                    'result_per_page']
                # data['results'] = myutils.ENTRY_SAMPLES

                data['form']['image'] = ''
                data['url_prefix_form'] = '&'.join([key + '=' + data['form'][key] for key in data['form'].keys()]) + '&'

                data['pagi']['cur_page'] = inputs['page']
                return render.gallery(data=data)
        else:
            return notfound(inputs)
            # data = {
            #     'form': myutils.FORM_INIT,
            #     'header': myutils.HEADER,
            #     'landing': myutils.LANDING_DATA_DEFAULT,
            # }
            # return render.index(data=data)


class gallery_poem:
    def GET(self):
        inputs = web.input()
        print (inputs)
        data = {
            'header': myutils.HEADER,
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
        print(inputs)
        filename = myutils.UPLOAD_PREFIX+inputs['filename']
        data = dict()

        objects, data['relu'] = getObjectFeature(filename)
        scene, attributes, data['heatmap'], data['ioscene'] = getSceneFeature(filename)

        # data['ioscene'] = 'ioscene'
        # data['heatmap'] = myutils.UPLOAD_PREFIX + filename
        # objects = ['a', 'b', 'c']
        # scene = ['a', 'b', 'c']
        # attributes = ['a', 'b', 'c']

        objectStr = ' ' + ', '.join([x[0] for x in objects])
        sceneStr = ' ' + ', '.join([x[0] for x in scene])
        attributesStr = ' ' + ', '.join(attributes)

        data['object'], data['scene'], data['emotion'] = objectStr, sceneStr, attributesStr
        data['label_complete'] = objects[0][0]

        # 对于 object,scene,emotion 这三个list中任何一个词word:
        word='悬崖'
        wordAssoList=associator.labelDict[word]
        wordAssoList=sorted(wordAssoList(key=lambda x:wordAssoList.index(x)*random()))
        print(wordAssoList[:10])
        #在用户点击某词时显示其关联古词，按权重随机取前10个


        # 以图生成现代诗的操作和之前一样

        # 以图搜索古代诗的方式就是通过226行的方法，用产生的联想词去搜，可以对每个词都联想，随机取

        # 以图生成古代诗就是对于得到的keywordList(长度至少为4，最好取8)，该keywordList可以如中烨所说，让用户选择
        print(gsw.genfromKeywords(wordAssoList))

        # 用户直接输入一句话，比如“日光照在青草上，今天天气真好”，生成古代诗，就是
        print(gsw.genfromSentence(self,"日光照在青草上，今天天气真好"))

        # 以上部分可能出现路径错误，需请调试，可先在gushiwenGenerate.py中看使用方法

        # print json.dumps(data)
        # return data
        # time.sleep(3)
        return json.dumps(data)


class matchimage:
    def GET(self):
        data = {
            'form': myutils.FORM_INIT,
            'header': myutils.HEADER,
            'footer': myutils.FOOTER,
        }
        return render.matchimage(data=data)

    def POST(self):
        inputs = web.input()
        print(inputs)
        data = {
            'imgurl': '/static/image/1.jpg'
        }
        return json.dumps(data)


class authorlist:
    def GET(self):
        inputs = web.input()
        data = {
            'form': myutils.FORM_INIT,
            'header': myutils.HEADER,
            'pagi': myutils.PAGI_SETTING,
            'footer': myutils.FOOTER,
        }

        validation = Validator.authorlist_validate(inputs)
        if validation == VALID_QUERY:
            try:
                inputs['page'] = int(inputs['page'])
            except:
                inputs['page'] = 1

            data['url_prefix_form'] = ''
            data['total_match'], data['results'] = PSES.search_author(cur_page=inputs['page'])
            data['pagi']['max_page'] = (data['total_match'] + data['pagi']['result_per_page'] - 1) // data['pagi'][
                'result_per_page']
            data['pagi']['cur_page'] = inputs['page']

            return render.authorlist(data=data)
        else:
            return notfound(inputs)

class authorpage:
    def GET(self):
        inputs = web.input()
        data = {
            'form': myutils.FORM_INIT,
            'header': myutils.HEADER,
            'pagi': myutils.PAGI_SETTING,
            'footer': myutils.FOOTER,
        }
        print (inputs)
        validation = Validator.authorpage_validate(inputs)
        if validation == VALID_QUERY:
            try:
                inputs['page'] = int(inputs['page'])
            except:
                inputs['page'] = 1
            data['desc'] = PSES.get_author_desc(inputs['author'])
            if data['desc'] == False:
                return notfound(inputs)
            data['url_prefix_form'] = 'author=' + inputs['author'] + '&'
            res = PSES.get_author_poems(inputs['author'], cur_page=inputs['page'], index='cnmodern')
            # print(res)
            if not res:
                res = PSES.get_author_poems(inputs['author'], cur_page=inputs['page'], index='gushiwen')
                # print(res)
            if not res:
                return notfound(inputs)

            data['total_match'], data['results'] = res
            print (data['total_match'], data['results'])
            data['pagi']['max_page'] = (data['total_match'] + data['pagi']['result_per_page'] - 1) // data['pagi'][
                'result_per_page']
            data['pagi']['cur_page'] = inputs['page']

            return render.authorpage(data=data)
        else:
            return notfound(inputs)


class poempage:
    def GET(self):
        inputs = web.input()
        data = {
            'form': myutils.FORM_INIT,
            'header': myutils.HEADER,
            'footer': myutils.FOOTER,
        }
        print(inputs)
        validation = Validator.poempage_validate(inputs)
        if validation == VALID_QUERY:
            data['result'] = PSES.get_poem(inputs)
            return render.poempage(data=data)
        else:
            return notfound(inputs)


class Validator:
    ancient_key_map = {
        'ancientAuthor': 'author',
        'ancientTime': 'dynasty',
        'ancientType': 'label_tokenized',
        'ancientLabel': 'label_tokenized',
        'ancientTitle': 'title_tokenized',
    }
    modern_key_map = {
        'modernTitle': 'title_tokenized',
        'modernAuthor': 'author',
        'modernLabel': 'label_tokenized',
        'modernStyle': 'style',
        'modernTime': 'time',
    }
    general_key_map = {
        'generalTitle': 'title_tokenized',
        'generalAuthor': 'author',
        'generalLabel': 'label_tokenized',
    }
    switch_key_map = {
        'author': 'author',
        'title': 'title_tokenized',
        'label': 'label_tokenized',
        'content': 'text_tokenized',
    }

    @staticmethod
    def authorlist_validate(input_dict):
        return  VALID_QUERY

    @staticmethod
    def authorpage_validate(input_dict):
        if 'author' in input_dict.keys() and input_dict['author']:
            return VALID_QUERY
        else:
            return INVALID_QUERY

    @staticmethod
    def poempage_validate(input_dict):
        if 'index' in input_dict.keys() and 'id' in input_dict.keys() and input_dict['index'] and input_dict['id']:
            return VALID_QUERY
        else:
            return INVALID_QUERY

    @staticmethod
    def form_validate(form_dict):
        flag = True
        for key in ['query', 'searchType']:
            flag = (flag and key in form_dict.keys())
        if not flag:
            print ('Failed! Invalid query 1!')
            return INVALID_QUERY
        if 'image' in form_dict.keys() and len(form_dict['image']) > 0:
            return VALID_IMAGE
        flag = False
        for key in ['query', 'ancientAuthor', 'ancientTime', 'ancientLabel', 'ancientTitle',
                    'modernTitle', 'modernAuthor', 'modernLabel', 'modernStyle',
                    'generalTitle', 'generalAuthor', 'generalLabel']:
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
                command_dict[Validator.switch_key_map[key]] = (input_dict['query'], False)
        command_dict['searchType'] = input_dict['searchType']
        if input_dict['searchType'] == 'ancient':
            if 'accurate' in input_dict.keys():
                # for key in ['ancientAuthor', 'ancientTime', 'ancientType', 'ancientLabel', 'ancientTitle']:
                for key in ['ancientAuthor', 'ancientTime', 'ancientLabel', 'ancientTitle']:
                    if input_dict[key] != '':
                        command_dict[Validator.ancient_key_map[key]] = (input_dict[key], True)
        elif input_dict['searchType'] == 'modern':
            if 'accurate' in input_dict.keys():
                for key in ['modernTitle', 'modernAuthor', 'modernLabel', 'modernStyle', 'modernTime']:
                    if input_dict[key] != '':
                        command_dict[Validator.modern_key_map[key]] = (input_dict[key], True)
        elif input_dict['searchType'] == 'all':
            if 'accurate' in input_dict.keys():
                for key in ['generalTitle', 'generalAuthor', 'generalLabel']:
                    if input_dict[key] != '':
                        command_dict[Validator.general_key_map[key]] = (input_dict[key], True)
        return command_dict


if __name__ == "__main__":
    sys.argv.append('8000')
    app = web.application(urls, globals())
    app.run()
