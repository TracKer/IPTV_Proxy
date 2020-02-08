import sys
from base64 import urlsafe_b64decode

from django.core.management.base import OutputWrapper
from django.views.generic.base import TemplateView

from main.core.SourceProcessor import SourceProcessor
from main.models import Source


class LinksContainerView(TemplateView):
    template_name = "LinksContainerView.html"

    def get_context_data(self, url: str, **kwargs):
        source = self.find_source(url)


        # context = super().get_context_data(**kwargs)
        context = {
            'url': urlsafe_b64decode(url).decode('ascii')
        }
        return context

    def find_source(self, url: str) -> Source:
        p = SourceProcessor(OutputWrapper(sys.stdout), url = url)
        p.update_source()
        return p.get_source()
