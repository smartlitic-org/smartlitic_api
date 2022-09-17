def save_index_template_as_composable(template, es_connector):
    template_body = template.to_dict()
    index_patterns = template_body.pop('index_patterns')
    order = template_body.pop('order', None)

    body = {
        'template': template_body,
        'index_patterns': index_patterns,
        'composed_of': [],
    }
    if order is not None:
        body['priority'] = order

    return es_connector.indices.put_index_template(name=template._template_name, body=body)
