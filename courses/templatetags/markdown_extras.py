import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def render_markdown(value):
    md = markdown.Markdown(extensions=['fenced_code', 'codehilite', 'tables', 'nl2br'])
    return mark_safe(md.convert(value))