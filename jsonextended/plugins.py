#!/usr/bin/env python


import os, glob, inspect
import imp
import uuid
from fnmatch import fnmatch

#py 2/3 compatibility
try:
    basestring
except NameError:
    basestring = str
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from jsonextended.utils import get_module_path

# list of plugin categories,
# and their minimal class attribute interface
# must include plugin_name
_plugins_interface = {
    'encoders':['plugin_name','objclass'],
    'decoders':['plugin_name','dict_signature'],
    'parsers': ['plugin_name','file_regex','read_file']}
    
# builtin plugin locations
from jsonextended import encoders, parsers
_plugins_builtin = [get_module_path(encoders),get_module_path(parsers)] 
                
# the internal plugin store
_all_plugins = {name:{} for name in _plugins_interface}

def view_interfaces(category=None):
    """ return a view of the plugin minimal class attribute interface(s)
    
    Properties
    ----------
    category : None or str
        if str, apply for single plugin category
    
    Examples
    --------
    
    >>> from pprint import pprint
    >>> pprint(view_interfaces())
    {'decoders': ['plugin_name', 'dict_signature'],
     'encoders': ['plugin_name', 'objclass'],
     'parsers': ['plugin_name', 'file_regex', 'read_file']}

    """
    if category is not None:
        return sorted(_plugins_interface[category][:])
    else:
        return {k:v[:] for k,v in _plugins_interface.items()}

def view_plugins(category=None):
    """ return a view of the loaded plugin names
    
    Properties
    ----------
    category : None or str
        if str, apply for single plugin category

    Examples
    --------
    
    >>> from pprint import pprint
    >>> pprint(view_plugins())
    {'decoders': [], 'encoders': [], 'parsers': []}

    >>> class DecoderPlugin(object):
    ...     plugin_name = 'example'
    ...     dict_signature = ('_example_',)
    ...
    >>> errors = load_plugin_classes([DecoderPlugin])

    >>> pprint(view_plugins())
    {'decoders': ['example'], 'encoders': [], 'parsers': []}
    >>> view_plugins('decoders')
    ['example']

    >>> unload_all_plugins()
    
    """
    dct = _all_plugins
    if not category is None:
        return [name for name,klass in _all_plugins[category].items()]
    else:
        return {cat:sorted([name for name,klass in plugins.items()]) for cat,plugins in _all_plugins.items()}
                        
def get_plugins(category):
    """ get plugins for category """
    return _all_plugins[category]
    
def unload_all_plugins(category=None):
    """ clear all plugins

    Properties
    ----------
    category : None or str
        if str, apply for single plugin category
    
    Examples
    --------
    
    >>> from pprint import pprint
    >>> pprint(view_plugins())
    {'decoders': [], 'encoders': [], 'parsers': []}

    >>> class DecoderPlugin(object):
    ...     plugin_name = 'example'
    ...     dict_signature = ('_example_',)
    ...
    >>> errors = load_plugin_classes([DecoderPlugin])

    >>> pprint(view_plugins())
    {'decoders': ['example'], 'encoders': [], 'parsers': []}
    >>> unload_all_plugins()
    >>> pprint(view_plugins())
    {'decoders': [], 'encoders': [], 'parsers': []}

    """
    if category is None:
        for cat in _all_plugins:
            _all_plugins[cat] = {}
    else:
        _all_plugins[category] = {}

def unload_plugin(name,category):
    """ remove single plugin 
    
    Properties
    ----------
    name : str
        plugin name
    category : str
        plugin category

    Examples
    --------
    
    >>> from pprint import pprint
    >>> pprint(view_plugins())
    {'decoders': [], 'encoders': [], 'parsers': []}

    >>> class DecoderPlugin(object):
    ...     plugin_name = 'example'
    ...     dict_signature = ('_example_',)
    ...
    >>> errors = load_plugin_classes([DecoderPlugin],category='decoders')

    >>> pprint(view_plugins())
    {'decoders': ['example'], 'encoders': [], 'parsers': []}
    >>> unload_plugin('example','decoders')
    >>> pprint(view_plugins())
    {'decoders': [], 'encoders': [], 'parsers': []}

    """
    _all_plugins[category].pop(name)

def load_plugin_classes(classes, category=None, overwrite=False):
    """ load plugins from class objects    

    Properties
    ----------
    category : None or str
        if str, apply for single plugin category
    overwrite : bool
        if True, allow existing plugins to be overwritten

    Examples
    --------
    
    >>> from pprint import pprint
    >>> pprint(view_plugins())
    {'decoders': [], 'encoders': [], 'parsers': []}

    >>> class DecoderPlugin(object):
    ...     plugin_name = 'example'
    ...     dict_signature = ('_example_',)
    ...
    >>> errors = load_plugin_classes([DecoderPlugin])

    >>> pprint(view_plugins())
    {'decoders': ['example'], 'encoders': [], 'parsers': []}

    >>> unload_all_plugins()

    """    
    load_errors = []
    for klass in classes:
        for pcat, pinterface in _plugins_interface.items():
            if category is not None and not pcat == category:
                continue
            if all([hasattr(klass,attr) for attr in pinterface]):
                if klass.plugin_name in _all_plugins[pcat] and not overwrite:
                    err = '{0} is already set for {1}'.format(klass.plugin_name,pcat)
                    load_errors.append(( str(pypath),'{}'.format(err) ))
                    continue
                _all_plugins[pcat][klass.plugin_name] = klass()
    return load_errors

def load_plugins_dir(path, category=None, overwrite=False):
    """ load plugins from a directory   
    
    Properties
    ----------
    category : None or str
        if str, apply for single plugin category
    overwrite : bool
        if True, allow existing plugins to be overwritten
 
    """    
    # get potential plugin python files
    if hasattr(path,'glob'):
        pypaths = path.glob('*.py')
    else:
        pypaths = glob.glob(os.path.join(path,'*.py')) 
    
    load_errors = []
    for pypath in pypaths:
        try:
            # use uuid to ensure no conflicts in name space
            module = imp.load_source(str(uuid.uuid4()),str(pypath))
        except Exception as err:
            load_errors.append(( str(pypath),'{}'.format(err) ))
            continue
        
        classes =  [klass for klass_name, klass in inspect.getmembers(module, inspect.isclass)]
        load_errors += load_plugin_classes(classes, category, overwrite)

    return load_errors

def load_builtin_plugins(category=None, overwrite=False):
    """load plugins from builtin directories
    
    Properties
    ----------
    category : None or str
        if str, apply for single plugin category

    Examples
    --------
    
    >>> from pprint import pprint
    >>> pprint(view_plugins())
    {'decoders': [], 'encoders': [], 'parsers': []}

    >>> errors = load_builtin_plugins()
    >>> errors
    []

    >>> pprint(view_plugins())
    {'decoders': ['decimal.Decimal',
                  'numpy.ndarray',
                  'pint.Quantity',
                  'python.set'],
     'encoders': ['decimal.Decimal',
                  'numpy.ndarray',
                  'pint.Quantity',
                  'python.set'],
     'parsers': ['crystal.out', 'json.basic']}

    >>> unload_all_plugins()    

    """
    load_errors = []
    for path in _plugins_builtin:
        load_errors += load_plugins_dir(path,category,overwrite=overwrite)
    return load_errors

def encode(obj, outtype='json', raise_error=False):
    """ encode objects, via encoder plugins, to new types
    
    Properties
    ----------
    outtype: str
        use encoder method to_<outtype> to encode
    raise_error : bool
        if True, raise ValueError if no suitable plugin found 
    
    Examples
    --------
    >>> load_builtin_plugins('encoders')
    []
    
    >>> from decimal import Decimal
    >>> encode(Decimal('1.3425345'))
    {'_python_Decimal_': '1.3425345'}
    >>> encode(Decimal('1.3425345'),outtype='str')
    '1.3425345'
    
    >>> encode(set([1,2,3,4,4]))
    {'_python_set_': [1, 2, 3, 4]}
    >>> encode(set([1,2,3,4,4]),outtype='str')
    '{1, 2, 3, 4}'
    
    >>> unload_all_plugins()    

    """            
    for encoder in get_plugins('encoders').values():
        if isinstance(obj, encoder.objclass) and hasattr(encoder, 'to_{}'.format(outtype)):
            return getattr(encoder,'to_{}'.format(outtype))(obj)
            break  
                
    if raise_error:
        raise ValueError('No JSON serializer is available for {0} (of type {1})'.format(obj,type(obj)))
    else:  
        return obj

def decode(dct, outtype='json', raise_error=False):
    """ decode dict objects, via decoder plugins, to new type
    
    Properties
    ----------
    outtype: str
        use decoder method from_<outtype> to encode
    raise_error : bool
        if True, raise ValueError if no suitable plugin found 
    
    Examples
    --------
    >>> load_builtin_plugins('decoders')
    []

    >>> from decimal import Decimal
    >>> decode({'_python_Decimal_':'1.3425345'})
    Decimal('1.3425345')

    >>> unload_all_plugins()    

    """            
    for decoder in get_plugins('decoders').values():
        if set(decoder.dict_signature).issubset(dct.keys()) and hasattr(decoder, 'from_{}'.format(outtype)):
            return getattr(decoder,'from_{}'.format(outtype))(dct)
            break  
              
    if raise_error:
        raise ValueError('no suitable plugin found for: {}'.format(dct))
    else:  
        return dct

def parser_available(fpath):
    """ test if parser plugin available for fpath
    
    Examples
    --------
    
    >>> load_builtin_plugins('parsers')
    []
    >>> test_file = StringIO('{"a":[1,2,3.4]}')
    >>> test_file.name = 'test.json'
    >>> parser_available(test_file)
    True
    >>> test_file.name = 'test.other'
    >>> parser_available(test_file)
    False
    
    >>> unload_all_plugins()    
    
    """
    if isinstance(fpath,basestring):
        fname = fpath
    elif hasattr(fpath, 'open') and hasattr(fpath, 'name'):
        fname = fpath.name
    elif hasattr(fpath, 'readline') and hasattr(fpath, 'name'):
        fname = fpath.name
    else:
        raise ValueError('fpath should be a str or file_like object: {}'.format(rfile))
    
    for parser in get_plugins('parsers').values():
        if fnmatch(fname,parser.file_regex):
            return True
                
    return False

def parse(fpath, **kwargs):
    """ parse file contents, via parser plugins, to dict like object
    NB: the longest file regex will be used from plugins
    
    Properties
    ----------
    fpath : file_like
         string, object with 'open' and 'name' attributes, or 
         object with 'readline' and 'name' attributes
    kwargs : keywords
        to pass to parser plugin
    
    Examples
    --------
    
    >>> load_builtin_plugins('parsers')
    []

    >>> from pprint import pformat

    >>> json_file = StringIO('{"a":[1,2,3.4]}')
    >>> json_file.name = 'test.json'
    
    >>> dct = parse(json_file)
    >>> print(pformat(dct).replace("u'","'"))
    {'a': [1, 2, 3.4]}
    
    >>> reset = json_file.seek(0)
    >>> from decimal import Decimal
    >>> dct = parse(json_file, parse_float=Decimal,other=1)
    >>> print(pformat(dct).replace("u'","'"))    
    {'a': [1, 2, Decimal('3.4')]}
    
    >>> class NewParser(object):
    ...     plugin_name = 'example'
    ...     file_regex = 'test.json'
    ...     def read_file(self, file_obj, **kwargs):
    ...         return {'example':1}
    >>> load_plugin_classes([NewParser],'parsers')
    []
    >>> reset = json_file.seek(0)
    >>> parse(json_file)
    {'example': 1}
    
    >>> unload_all_plugins()    

    """            
    if isinstance(fpath,basestring):
        fname = fpath
    elif hasattr(fpath, 'open') and hasattr(fpath, 'name'):
        fname = fpath.name
    elif hasattr(fpath, 'readline') and hasattr(fpath, 'name'):
        fname = fpath.name
    else:
        raise ValueError('fpath should be a str or file_like object: {}'.format(rfile))
    
    parser_dict = {plugin.file_regex:plugin for plugin in get_plugins('parsers').values()}
    
    # find longest match first
    for regex in sorted(parser_dict.keys(),key=len,reverse=True):
        parser = parser_dict[regex]
        if fnmatch(fname,regex):
            if isinstance(fpath,basestring):
                with open(fpath,'r') as file_obj:
                    data = parser.read_file(file_obj, **kwargs)
            elif hasattr(fpath, 'open'):
                with fpath.open('r') as file_obj:
                    data = parser.read_file(file_obj, **kwargs)            
            elif hasattr(fpath, 'readline'):
                data = parser.read_file(fpath, **kwargs)            
            return data
                
    raise ValueError('{} does not match any regex'.format(fname))

    