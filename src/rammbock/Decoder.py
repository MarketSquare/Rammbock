import imp

def string2object(message, data):
    application_protocol = 'http'
    version = '1_1'
    headers_schema = imp.load_source('HeaderSchema', "src/rammbock/protocols/"+application_protocol+"/"+version+".py")
    header_schema = headers_schema.HeaderSchema('http_get')
    schema = header_schema.headers
    splitted = data.split()
    _get_headers_from_list(message, splitted[:len(schema)], schema)
    _get_ies_from_list(message,splitted[len(schema):])

def _get_headers_from_list(message, all_headers, headers_schema):
    message.header += [[headers_schema[i], all_headers[i]] for i in range(len(headers_schema))]
        
def _get_ies_from_list(message, splitted):
    message.ie += [[splitted[i][:-1], splitted[i+1]] for i in range(0,len(splitted),2)]
