# Translated Page Renderer

The purpose of this application is to combine HTML templates with translation files to render out different versions
of the same page, each in a different language.

## Features

* Templates and translations are requested from customizable providers
* Renderer supports the addition of filters to apply fixes or formatting to the injected text blocks

## Open Tasks

* [ ] Fix handling of the `<html><body>` wrapper that is added by `etree.HTML()`
* [ ] Add filter for Markdown conversion (according to the rules currently in place for the FAH translation project)
* [ ] Provide sample providers that can locate templates and translations as currently stored in the FAH project
* [ ] Find a smarter way to write tests that compare HTML (to e.g. avoid issues with the different encoding)