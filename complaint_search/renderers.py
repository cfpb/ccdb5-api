from rest_framework.renderers import BaseRenderer, JSONRenderer


class DefaultRenderer(JSONRenderer):
    format = "default"


class CSVRenderer(BaseRenderer):
    media_type = "text/csv"
    format = "csv"

    def render(self, data, media_type=None, renderer_context=None):
        return data
