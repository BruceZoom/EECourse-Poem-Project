import website

render = web.template.render('templates')

urls = (
	'', 'index'
)

display_utils = {
	
}


class index:
	def GET(self):
		data = {

		}
		return render.index(data=data)
