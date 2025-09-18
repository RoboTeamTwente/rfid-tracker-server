from django import template
from django.urls import reverse
from django.utils.html import format_html

register = template.Library()


@register.simple_block_tag(takes_context=True)
def modal(context, content, title, *args, **kwargs):
    html = """
    <div class="modal">
      <form class="modal__content" method="POST" action="{action}" >
        <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
        <h2 class="modal__title">{title}</h2>
        {content}
      </form>
    </div>
    """
    return format_html(
        html,
        content=content,
        title=title,
        action=reverse(*args, **kwargs),
        csrf_token=context.get('csrf_token'),
    )
