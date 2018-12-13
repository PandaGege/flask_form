# coding:utf8

from flask import Blueprint, request, g, current_app, jsonify

from flask_form import (option, ChoiceType, IntRangeType, IntType, InputType,
        TextAreaType, CheckBoxType, RadioType, OptionType, TagItems)
from flask_form import form as decorator_form


bp = Blueprint('form', __name__, url_prefix='/form')


@bp.errorhandler(500)
def internel_error(e):
    return 'form 500 page', 500


sex = TagItems()
sex.add('male', '男')
sex.add('female', '女')

interest = TagItems()
interest.add('football', '足球')
interest.add('Basketball')
interest.add('Swimming')
interest.add('sing')

hts = ['河北', '北京', '天津', '重庆', '广州']
hometown = TagItems()
for ht in hts:
    hometown.add(ht, ht)


@bp.route('/sign_up', methods=['GET', 'POST'])
@decorator_form(need_html=True, method='GET')
@option('nickname', form_type='input', value_type=bytes, default='regan')
@option('email', form_type=InputType, value_type=unicode, callback=email_check)
@option('age', form_type=InputType('text'), value_type=IntType)
@option('passwd', form_type=InputType('password'), value_type=unicode)
@option('sex', form_type=RadioType(sex), value_type=str, default='male')
@option('interest', form_type=CheckBoxType(interest), value_type=unicode,
        default=['football', 'sing'])
@option('hometown', form_type=OptionType(hometown), value_type='unicode',
        default=['重庆'])
def sign_up():
    return 'hello world'


