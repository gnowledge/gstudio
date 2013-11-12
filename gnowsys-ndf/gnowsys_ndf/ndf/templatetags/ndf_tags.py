from django import template

register = template.Library()

@register.inclusion_tag('ndf/edit_content.html', takes_context=True)
def edit_content(context):
  
  request = context['request']
  user = request.user
  
  doc_obj = context['node']
  
  return {'template': 'ndf/edit_content.html', 'user': user, 'node': doc_obj}
