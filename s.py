# coding: utf-8
# ----------------------------------------------
# author            : regan
# email             : x-regan@qq.com
# create at         : 2018-09-07 14:35
# last modify       : 2018-09-07 14:35
# ----------------------------------------------



from flask_form import ready, option, ChoiceType, IntRangeType
from flask_form import InputType, TextAreaType, CheckBoxType, \
                        RadioType, OptionType
from flask import Flask, request, render_template
from flask_form import TagItems


app = Flask(__name__)

cb = TagItems(['1992', '1993', '1994', '1995'])

rd = TagItems()
rd.add('male', u'男')
rd.add('female', u'女')

op = TagItems()
op.add('one', u'一')
op.add('two', u'二')
op.add('three', u'三')

@app.route('/', methods=['POST', 'GET'])
@ready(need_html=True, method='post', action='#')
@option('user', form_type=InputType('text'), value_type=bytes, default='regan')
@option('num', form_type=InputType('text'), value_type=int, default=1)
@option('password', form_type=InputType('password'), value_type=unicode)
@option('txta', form_type=TextAreaType, value_type=unicode)
@option('cb', form_type=CheckBoxType(items=cb), value_type=str)
@option('rd', form_type=RadioType(rd), value_type=str)
@option('op', form_type=OptionType(op), value_type=str)
def index(query, html):
    print request.method
    print query
    print request.form
    print html
    return render_template('test.html', form=html)


if __name__ == '__main__':
    app.debug = True
    app.run(threaded=True, host='0.0.0.0', port=11111)
