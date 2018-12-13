# coding: utf-8
# ----------------------------------------------
# author            : regan
# email             : x-regan@qq.com
# create at         : 2018-09-02 13:51
# last modify       : 2018-09-02 20:33
# ----------------------------------------------


'''
用来解析请求参数并生成form表单信息的工具
暂时只适用于flask
生成的form表单信息可用于传递给flask templates

flask和jinja完全基于unicode，所以输入输出文本默认皆为unicode
'''

import sys
import six
import types
from collections import namedtuple, OrderedDict
from flask import request


__all__ = [
        'IntType', 'FloatType', 'BoolType', 'BytesType', 'UnicodeType',
        'ChoiceType', 'IntRangeType',
        'InputType', 'TextareaType', 'CheckboxType',
        'RadioType', 'OptionType', 'TagItems',
        'form', 'option',
    ]


def to_unicode(text, encoding=None, errors='strict'):
    """Return the unicode representation of a bytes object `text`. If `text`
    is already an unicode object, return it as-is."""
    if isinstance(text, six.text_type):
        return text
    if not isinstance(text, (bytes, six.text_type)):
        raise TypeError('to_unicode must receive a bytes, str or unicode '
                        'object, got %s' % type(text).__name__)
    if encoding is None:
        encoding = 'utf-8'
    return text.decode(encoding, errors)


def to_bytes(text, encoding=None, errors='strict'):
    """Return the binary representation of `text`. If `text`
    is already a bytes object, return it as-is."""
    if isinstance(text, bytes):
        return text
    if not isinstance(text, six.string_types):
        raise TypeError('to_bytes must receive a unicode, str or bytes '
                        'object, got %s' % type(text).__name__)
    if encoding is None:
        encoding = 'utf-8'
    return text.encode(encoding, errors)


def any_to_unicode(val, encoding='utf-8', errors='strict'):
    if not val:
        return u''
    if isinstance(val, six.text_type):
        return val
    if isinstance(val, bytes):
        try:
            return val.decode(encoding, errors)
        except:
            pass
    # 强制转换, 转换失败则raise error
    if six.PY2:
        return unicode(val)
    if six.PY3:
        return str(val)


class TagItems(object):
    def __init__(self, items=None):
        '''
            items为list或tuple
                成员为dict, 键值对见self.add的参数
                成员为text, 则默认为item的name
        '''

        self.items = OrderedDict()
        if items:
            if isinstance(items, (tuple, list)):
                for item in items:
                    if isinstance(item, dict):
                        self.add(**item)
                    elif isinstance(item, (int, six.binary_type, six.text_type)):
                        self.add(any_to_unicode(item))
                    else:
                        raise ValueError('unsupported the type of item')
            else:
                raise ValueError('items`type must be list or tuple')

    def __iter__(self):
        return iter([ v for k, v in self.items.items()])

    def add(self, value, show=None, **extra):
        item = {}
        item['value'] = any_to_unicode(value)
        item['show'] = any_to_unicode(show)
        if not show:
            item['show'] = value
        item['extra'] = extra
        self.items[value] = item

    def __getitem__(self, key):
        return self.items.get(key)


class ParamType(object):
    name = None

    def __call__(self, val, param=None):
        if val is not None:
            return self.convert(val)

    def convert(self, val):
        return val

    def __str__(self):
        return self.name.upper()

    def __repr__(self):
        return self.name.upper()


class IntType(ParamType):
    name = 'int'

    def convert(self, val, param=None):
        # 失败直接raise Error
        return int(val)


class FloatType(ParamType):
    name = 'float'

    def convert(self, val, param=None):
        # 失败直接raise Error
        return float(val)


class BoolType(ParamType):
    name = 'boolean'

    def convert(self, val, param=None):
        if isinstance(val, bool):
            return bool(val)
        val = val.lower()
        if val in ('true', '1', 'yes', 'y'):
            return True
        if val in ('false', '0', 'no', 'n'):
            return False
        raise ValueError('can`t convert "{0}" to bool'.format(val))


class BytesType(ParamType):
    '''在python2中是str; 在Python3中是bytes
    '''
    name = 'bytes'

    def __init__(self, encoding='utf8'):
        self.ec = encoding

    def convert(self, val, param=None):
        return to_bytes(val, self.ec)


class UnicodeType(ParamType):
    '''在Python2中是unicode, Python3中是str
    '''
    name = 'unicode'

    def __init__(self, encoding='utf8'):
        self.ec = encoding

    def convert(self, val, param=None):
        return to_unicode(val, self.ec)


class ChoiceType(ParamType):
    name = 'choice'

    def __init__(self, choice):
        self.choice = choice

    def convert(self, val, param=None):
        if val in self.choice:
            return val


class IntRangeType(ParamType):
    '''整型区间，min, max为空，则表示那一端不限制
    clamp为True时：超出范围时取端点的值
    '''
    name = 'int range'

    def __init__(self, min=None, max=None, clamp=False):
        self.min = min
        self.max = max
        self.clamp = clamp

    def convert(self, val, param=None):
        val = IntType().convert(val)
        if self.clamp:
            if self.min is not None and val < self.min:
                return self.min
            if self.max is not None and val > self.max:
                return self.max
        if self.min is not None and val < self.min or \
           self.max is not None and val > self.max:
            raise ValueError('{} not in ({}, {})'.format(val, self.min,
                             self.max))
        return val


tmp = namedtuple('_', ('int', 'float', 'bool', 'bytes', 'str', 'unicode', 'choice',
                       'intrange'))
if six.PY2:
    strtype = BytesType
if six.PY3:
    strtype = UnicodeType

    
ParamTypes = tmp(int=IntType,
                 float=FloatType,
                 bool=BoolType,
                 bytes=BytesType,
                 str=strtype,
                 unicode=UnicodeType,
                 choice=ChoiceType,
                 intrange=IntRangeType,
                 )
del tmp


class FormType(object):
    '''Form表单字段类型基类, 输出字符串皆为unicode类型
    '''
    name = None

    def __init__(self, **kwargs):
        self.field_type = self.name
        self.extra = kwargs

    def __call__(self, parm_val):
        return self.convert_value(parm_val)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def convert_value(self, val):
        return any_to_unicode(val)


class InputType(FormType):
    '''输入框, 类型有button, file, hidden, image, password, radio,
            reset, submit, text
        text:      文本输入框
        button:    定义可点击的按钮，但没有任何行为。button
                   类型常用于在用户点击按钮时启动 JavaScript 程序。
        file:      用于文件上传。
        hidden:    定义隐藏字段。隐藏字段对于用户是不可见的。
                   隐藏字段通常会存储一个默认值，它们的值也可以由JavaScript
                   进行修改。
        image:     定义图像形式的提交按钮。
        password:  密码
        reset:     重置按钮会清除表单中的所有数据。
        submit:    提交

        InputType不处理type为checkbox, radio的input, 分别由CheckBoxType,
            RadioType处理
    '''
    name = u'input'

    def __init__(self, type='text', **kwargs):
        super(InputType, self).__init__(**kwargs)
        self.input_type = type


class TextAreaType(FormType):
    '''文本域
    '''
    name = 'textarea'


class CheckBoxType(FormType):
    '''复选框
        items: list(value[, checked[, name[, extra]]])
            checked: bool, default False
            name: 选项显示值，default value
            extra 为dict类型, css样式等
    '''
    name = 'checkbox'
    multiple = True

    def __init__(self, items, **kwargs):
        super(CheckBoxType, self).__init__(**kwargs)
        self.items = items
        # items和dict的items方法同名, 在jinja中无法通过对象属性方式访问
        # so: 重命名为entries
        self.entries = items

    def is_checked(self, item, values):
        # 不够优雅，待优化
        if item['value'] in values:
            return True
        return False

    def convert_value(self, values):
        vals = set()
        if values:
            for v in values:
                vals.add(any_to_unicode(v))
        return vals


class RadioType(CheckBoxType):
    '''单选按钮, 
    '''
    name = 'radio'
    multiple = False

    def __init__(self, items, **kwargs):
        super(RadioType, self).__init__(items, **kwargs)

    def convert_value(self, values):
        vals = set()
        if values:
            vals.add(any_to_unicode(values))
        return vals


class OptionType(CheckBoxType):
    '''下拉列表
    '''
    name = 'option'
    multiple = False

    def __init__(self, items, **kwargs):
        super(OptionType, self).__init__(items, **kwargs)

    def convert_value(self, values):
        vals = set()
        if values:
            vals.add(any_to_unicode(values))
        return vals


tmp = namedtuple('_', ('input', 'textarea', 'checkbox', 'radio', 'option')
                 )
FormTypes = tmp(input=InputType,
                textarea=TextAreaType,
                checkbox=CheckBoxType,
                radio=RadioType,
                option=OptionType,
                )
del tmp


class Option(object):
    '''
    name: 字段名
    type: 表单字段类型，input, textarea...
    value_type: 字段值的类型. ParamType的子类, 或python内置类型int, float,
        boolean, str, unicode
    default: 表单字段的默认值
    nullable: 是否可为空，
    callback: 执行回调做一些预处理, 如合法性检测
    extra: 其它想传递给html模板的键值对, 比如需特别指明的styles样式
    callback 先于其他逻辑, 参数request参数值
    multiple: 多个值时，返回list, item的类型为value_type指定的，默认为False.
        当form_type是CheckBox是默认为True，且只能为True
    '''
    def __init__(self, name, form_type=None, value_type=UnicodeType, default=None,
                 nullable=True, callback=None, multiple=False, **extra):
        self.name = name
        self.form_type = self.convert_form_type(form_type)
        self.value_type = self.convert_value_type(value_type)
        self.default = default
        self.nullable = nullable
        self.callback = callback
        self.extra = extra
        self.multiple = multiple
        if isinstance(self.form_type, CheckBoxType):
            self.multiple = self.form_type.multiple

    def convert_form_type(self, ty):
        if isinstance(ty, FormType):
            return ty
        if isinstance(ty, (six.binary_type, six.text_type)):
            if hasattr(FormTypes, ty.lower()):
                t = getattr(FormTypes, ty.lower())
                ty = t()
                return ty
        if isinstance(ty, type) and issubclass(ty, FormType):
            return ty()
        # form_type可为空，因为有时候不需要form表单，比如用于接口时
        if not ty:
            return None
        raise TypeError('Unknown value type')

    def convert_value_type(self, ty):
        if isinstance(ty, ParamType):
            return ty
        if isinstance(ty, (six.binary_type, six.text_type)):
            if hasattr(ParamTypes, ty.lower()):
                t = getattr(ParamTypes, ty.lower())
                ty = t()
                return ty
        if isinstance(ty, type):
            if issubclass(ty, ParamType):
                return ty()
            if ty is int:
                return IntType()
            if ty is float:
                return FloatType()
            if ty is bool:
                return BoolType()
            if ty is six.text_type:
                return UnicodeType()
            if ty is six.binary_type:
                return BytesType()
        raise TypeError('Unknown value type')

    def cast_value(self, income_value):
        # callback 在哪一步执行比较好？这是个问题？暂时放在最后
        # callback参数为参数值，返回值为最终传递给用户代码的值
        # callback可用于参数预处理，和raise error
        # cast by value_type >  default > nullable > callback 
        # 1, 先用参数类型转换值
        # 2, 如果为空则用default值代替
        # 3, 校验是否为空
        # 4, callback返回装饰过的值、或者raise error
        vals = []
        if income_value:
            for iv in income_value:
                if iv:
                    val = self.value_type(iv, self.name)
                    vals.append(val)
        if not vals and self.default:
            if isinstance(self.default, list):
                vals.extend(self.default)
            else:
                vals.append(self.default)
        if not vals and self.nullable is False:
            raise ValueError('{} can not be null'.format(self.name))
        if self.multiple:
            value = vals
        elif vals:
            value = vals[0]
        else:
            value = None
        if self.callback is not None:
            return self.callback(value)
        return value

    def gen_html(self, val=None):
        html = {}
        val = self.form_type(val)
        html['name'] = self.name
        html['value'] = val
        html['taginfo'] = self.form_type
        return html


class ReqInfo(object):
    def __init__(self):
        self._query = OrderedDict()
        self._exception = None
        self._traceback = None
        self._html = OrderedDict()

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        if value.lower() not in ('get', 'post'):
            raise ValueError('Unsupported methods: {}'.format(value))
        self._method = value

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        self._action= value

    def set_query(self, name, val):
        self._query[name] = val

    def set_html(self, name, val):
        self._html[name] = val

    def if_raise(self):
        if self._exception:
            if isinstance(self._exception, types.InstanceType):
                # The exception is an instance of an old-style class, which
                # means type(self._exception) returns types.ClassType instead
                # of the exception's actual class type.
                exception_type = self._exception.__class__
            else:
                exception_type = type(self._exception)
            raise exception_type, self._exception, self._traceback

    @property
    def query(self):
        self.if_raise()
        return self._query

    @property
    def html(self):
        self.if_raise()
        return {'method': self._method,
                'action': self._action,
                'parms': self._html}

    def set_exception(self, e, tb):
        self._exception = e
        self._traceback = tb


class Form(object):
    '''
        f:装饰器修饰的方法
        method: 即form的method
        action: 即form的action
        need_html: 是否需要var_html参数
    '''
    def __init__(self, f, method='post', action='#', need_html=False):
        self.__name__ = f.__name__
        self.__doc__ = f.__doc__
        self.f = f
        # 按字段配置顺序
        self.f.__forms__.reverse()
        self.need_html = need_html
        method = method.lower()
        if method not in ('post', 'get'):
            raise ValueError('unsupported http method')
        self.method = method
        self.action = action

    def _request_query(self):
        if request.method == 'GET':
            params = request.args
        if request.method == 'POST':
            params = request.form
        return dict(params.lists())

    def main(self, info):
        info.method = self.method
        info.action = self.action
        opts = self.f.__forms__
        params = self._request_query()
        for opt in opts:
            name = opt.name
            income_val = params.get(name)
            val = opt.cast_value(income_val)
            info.set_query(name, val)
            if self.need_html:
                h = opt.gen_html(val)
                info.set_html(name, h)
        return info

    def __call__(self, *args, **kwargs):
        info = ReqInfo()
        try:
            self.main(info)
        except:
            e, tb = sys.exc_info()[1:]
            info.set_exception(e, tb)
        # request实例在请求处理期间可用，so可以把结果绑定到request上
        request.flask_form = info
        return self.f(*args, **kwargs)


def form(*args, **kwargs):
    def decorator(f):
        return Form(f, *args, **kwargs)
    return decorator


def option(*args, **kwargs):
    def decorator(f):
        opt = Option(*args, **kwargs)
        if not hasattr(f, '__forms__'):
            f.__forms__ = []
        f.__forms__.append(opt)
        return f
    return decorator
