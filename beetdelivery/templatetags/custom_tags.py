from django import template

register = template.Library()

@register.filter
def as_row(form):
    """
    Custom filter to display form fields in a well-shaped row.
    """
    html = ""
    for field in form:
        html += f'<div class="form-row">{field.label_tag()} {field}{field.errors}</div>'
    print(html)
    return html

@register.filter(name='is_manager')
def is_manager(obj):
    ans = hasattr(obj, 'manager')
    return ans

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)