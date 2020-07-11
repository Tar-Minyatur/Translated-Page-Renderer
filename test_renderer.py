from unittest import TestCase
from unittest.mock import patch

from lxml import etree

from renderer import TranslationProvider, TemplateProvider, Renderer, TemplateNotFoundException, \
    MissingTranslationException


class RendererTest(TestCase):

    def setUp(self) -> None:
        super().setUp()

    def test_render_replaces_text(self) -> None:
        self._run_test(
            given_template='<html><body><p><fah-text>Just some Text</fah-text></p></body></html>',
            given_translations=['Nur etwas Text'],
            given_translation_ids=['Just some Text'],
            expected_html='<html><body><p>Nur etwas Text</p></body></html>')

    def test_render_leaves_unmarked_text_untouched(self) -> None:
        self._run_test(
            given_template='<html><body><p>Random Text</p></body></html>',
            expected_html='<html><body><p>Random Text</p></body></html>')

    def test_render_fails_if_template_is_missing(self) -> None:
        with patch.object(TemplateProvider, 'get_template', return_value=None) as template:
            renderer = Renderer(template_provider=TemplateProvider(), translation_provider=TranslationProvider())
            self.assertRaises(TemplateNotFoundException, renderer.render, 'unknown_page', 'any')
            template.assert_called_with('unknown_page')

    def test_render_fails_if_translation_cannot_be_found(self) -> None:
        with patch.object(TemplateProvider, 'get_template',
                          return_value=etree.HTML('<p><fah-text>Unknown Text</fah-text></p>')) as template, \
                patch.object(TranslationProvider, 'translate', return_value=None) as translate:
            renderer = Renderer(template_provider=TemplateProvider(), translation_provider=TranslationProvider())
            self.assertRaises(MissingTranslationException, renderer.render, 'some_page', 'any')
            template.assert_called_with('some_page')
            translate.assert_called_with('any', 'Unknown Text')

    # This test currently fails because:
    # * `etree.HTML()` adds `<html>` and `<body>` tags around HTML fragments
    # * Special characters are encoded as HTML entities in the output from `etree.tostring()`
    def test_render_with_complex_template(self) -> None:
        self._run_test(
            given_template="""<div>
                <header><h1><fah-text>Page Title</fah-text></h1></header>
                <section>
                    <h2><fah-text>Subtitle</fah-text></h2>
                    <p><fah-text>This sections contains some text.</fah-text></p>
                </section>
            </div>""",
            given_translations=['Seitentitel', 'Untertitel', 'Dieser Bereich enthält etwas Text.'],
            given_translation_ids=['Page Title', 'Subtitle', 'This sections contains some text.'],
            expected_html="""<div>
                <header><h1>Seitentitel</h1></header>
                <section>
                    <h2>Untertitel</h2>
                    <p>Dieser Bereich enthält etwas Text.</p>
                </section>
            </div>"""
        )

    def _run_test(self, given_template: str,
                  expected_html: str,
                  given_translations: list = None,
                  given_translation_ids: list = None) -> None:

        # Given
        with patch.object(TemplateProvider, 'get_template', return_value=etree.HTML(given_template)) as get_template, \
                patch.object(TranslationProvider, 'translate', side_effect=given_translations) as translate:
            renderer = Renderer(template_provider=TemplateProvider(), translation_provider=TranslationProvider())

            # When
            html = renderer.render('test_page', 'any')

            # Then
            self.assertEqual(expected_html.encode('UTF-8'), html)
            get_template.assert_called_with('test_page')
            if given_translation_ids is None or len(given_translation_ids) == 0:
                translate.assert_not_called()
            else:
                for translation_id in given_translation_ids:
                    translate.assert_any_call('any', translation_id)
