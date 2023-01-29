from django import template

register=template.Library()

@register.filter(name='br')
def br(data, each_number):
    counter = 0
    html = ''

    for elem in data:

        if counter % each_number == 0 and counter != 0 :
            html += "<br>" + elem
            counter += 1
        else:
            html += elem
        counter += 1

    return html