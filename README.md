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

## Context

### Architecture Overview

This is a rough overview of a possible plan to tackle the entire FAH translation project. The current scope of the application in this repository is outlined in red:

![FAH Translation Project Architecture Overview](https://github.com/Tar-Minyatur/Translated-Page-Renderer/blob/master/docs/fah-translation-architecture-overview.svg)

### Assumptions

We currently design the solution for the translation system with the current assumptions in mind:

* No custom plugin for Wordpress, but instead we build a standalone system that integrates through the Wordpress API
* We don't want to interfere with the editorial side of things and not put any restrictions on how pages can be designed within Wordpress

### Process Proposal

This is how I currently imagine the process to work on a high level:

1. *Automated:* We export the raw HTML content for all relevant posts/pages from Wordpress through the Wordpress API
2. *Automated:* For each page we create an HTML file containing the original post content and push all of them to a new branch in a GitHub repository
3. *Automated, Optional:* The extractor component runs a first conversion on the files and isolates the text blocks to be translated, surrounds them with `<fah-text>` and writes the texts as message IDs into the corresponding .po file
4. *Manual:* Someone from the project team goes through the template files and cleans up the message IDs, ensures that all of them make sense and don't break any of the layout or mess with the shortcodes in the content (e.g. `[vc_column]` etc.)
5. *Semi-Automated:* When they are ready, the templates are merged into master of the template repository and the new translation files are pushed into the Translate repository
6. *Automated:* To generate/update the translated pages in Wordpress, a rendering component pulls the templates from one and the translation files from the second repository, replaces all occurences of `<fah-text>` with the corresponding text blocks and provides the rendered HTML
7. *Automated:* The Wordpress API integration component checks for existing pages and either updates them or creates new ones

### Current Challenges

* The Wordpress API returns the posts/pages in a semi-rendered state.
  * There is a surprising amount of HTML code generated by the social plugin FAH is using within the actual post content.
  * The content is also a mix of HTML and so-called "shortcodes", e.g. `[vc_column]`, which trigger some special rendering when Wordpress actually outputs the page to visitors.
  * As these are not HTML tags, they cannot be identified semantically by parsing the HTML into a DOM document. There is a high likelihood that they get mixed up with the actual text blocks.
  * It is in theory of course possible to write a parser that recognizes these shortcodes and preserves them without including them in the translation messages, but it would require replicating logic we actually don't need.
* We need to find the right balance between automation and not rolling out confusing or overly complicated translation files to the translation teams.
  * We agreed to try to avoid splitting up text blocks as much as possible.
  * To do so, we want to use Markdown for simple inline formatting.
  * Generating these text block automatically is a bit challenging and a potential source of errors.
* All in all it seems unlikely that we will be able to build a fully automated extraction mechanism that perfectly converts the raw posts from Wordpress into translation files and templates in one go without messing up at least some message IDs.
  * It would be a lot easier to have the text blocks marked earlier in the process, i.e. during the design phase.
  * Alternatively, aligning more closely how pages will be built and what the translation system would have to support would make the decision-making process easier.
