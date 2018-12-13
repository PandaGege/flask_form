# coding: utf-8
# ----------------------------------------------
# author            : regan
# email             : x-regan@qq.com
# create at         : 2018-09-07 14:35
# last modify       : 2018-09-07 14:35
# ----------------------------------------------



from flask_form import form, option, ChoiceType, IntRangeType
from flask_form import InputType, TextAreaType, CheckBoxType, \
                        RadioType, OptionType
from flask import Flask, request, render_template, jsonify
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
@form(need_html=True, method='post', action='#')
@option('user', form_type=InputType('text'), value_type=bytes, default='regan')
@option('num', form_type=InputType('text'), value_type=int, default=1)
@option('password', form_type=InputType('password'), value_type=unicode)
@option('txta', form_type=TextAreaType, value_type=unicode)
@option('cb', form_type=CheckBoxType(items=cb), value_type=str, default=['1992', '1993'])
@option('rd', form_type=RadioType(rd), value_type=str, default=['female'])
@option('op', form_type=OptionType(op), value_type=str, default=['two'])
@option('choice', form_type=InputType('text'),
        value_type=ChoiceType(['1','2']), nullable=True)
def index():
    print request.query
    print request.form
    print request.html
    return render_template('test.html', form=request.html)


@app.route('/jsont/', methods=['get'])
@form(need_html=False)
@option('aaa')
@option('bbb')
@option('ccc', value_type=int)
def jsont():
    print request.args
    print request.method
    print request.query
    print request.form
    s = {'a': 'a', 'b': 1, 'c': 222}
    return jsonify(s)


if __name__ == '__main__':
    app.debug = True
    app.run(threaded=True, host='0.0.0.0', port=11111)
