from lxml import etree


class TemplateProvider:
    """Locates and returns the right HTML template for a given website, indicated by its page name."""

    def get_template(self, page_name: str) -> etree.ElementTree:
        raise NotImplementedError("This class needs to be inherited to provide actual functionality")


class TranslationProvider:
    """Locates and returns translated strings for a given language and text block identifier."""

    def translate(self, language_id: str, text_block_id: str) -> str:
        raise NotImplementedError("This class needs to be inherited to provide actual functionality")


class TextFilter:
    """Will be applied to any inserted translation. This is meant to be used e.g. to apply inline formatting."""

    def apply(self, text: str) -> str:
        return text


class TemplateNotFoundException(Exception):
    def __init__(self, error_message):
        super(TemplateNotFoundException, self).__init__(error_message)


class MissingTranslationException(Exception):
    def __init__(self, error_message):
        super(MissingTranslationException, self).__init__(error_message)


class Renderer:
    TAG_NAME = 'fah-text'

    def __init__(self, template_provider: TemplateProvider,
                 translation_provider: TranslationProvider,
                 text_filters: list = None):
        self._template_provider = template_provider
        self._translation_provider = translation_provider
        self._text_filters = text_filters if isinstance(text_filters, list) else []

    def add_filter(self, text_filter: TextFilter) -> None:
        self._text_filters.append(text_filter)

    def _get_text_block_tag_name(self) -> str:
        return self.TAG_NAME

    def render(self, page_name: str, language_id: str) -> str:
        template = self._template_provider.get_template(page_name)
        if template is None:
            raise TemplateNotFoundException(f"Template for page '{page_name}' could not be located")
        for node in template.xpath(f'//{self._get_text_block_tag_name()}'):
            translation = self._translation_provider.translate(language_id, node.text)
            if translation is None:
                raise MissingTranslationException(f"Could not find translation in language {language_id} for: {node.text}")
            parent_node = node.getparent()
            parent_node.remove(node)
            parent_node.text = self._apply_filters(translation)
        return etree.tostring(template, method='html')

    def _apply_filters(self, text) -> str:
        for text_filter in self._text_filters:
            text = text_filter.apply(text)
        return text

