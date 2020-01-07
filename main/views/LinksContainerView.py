from base64 import urlsafe_b64decode

from django.views.generic.base import TemplateView


class LinksContainerView(TemplateView):
    template_name = "LinksContainerView.html"

    def get_context_data(self, url: str, **kwargs):
        # context = super().get_context_data(**kwargs)
        context = {
            'url': urlsafe_b64decode(url).decode('ascii')
        }
        return context
