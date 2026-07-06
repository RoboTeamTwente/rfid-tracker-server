from django import template
from django.urls import reverse
from django.utils.html import format_html

register = template.Library()


@register.simple_block_tag(takes_context=True)
def modal(context, content, id, target, title):
    if context.request.GET.get('modal') != id:
        return format_html('<div id="modal-{id}"></div>', id=id)

    # redirect back to the same page, but with the modal closed
    qs = context.request.GET.copy()
    qs.pop('modal')
    next = context.request.path + '?' + qs.urlencode()

    html = """
    <div class="modal" id="modal-{id}">
      <form class="modal__content" method="POST" action="{action}">
        <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
        <input type="hidden" name="next" value="{next}">
        <h2 class="modal__title">{title}</h2>
        {content}
      </form>
    </div>
    """
    return format_html(
        html,
        id=id,
        content=content,
        title=title,
        action=reverse(target),
        next=next,
        csrf_token=context.get('csrf_token'),
    )
