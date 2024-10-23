from django import template
from django.utils.safestring import mark_safe
from markdown import markdown as convert_markdown
from bleach import Cleaner
from bleach.linkifier import LinkifyFilter
from django.utils.html import escape
from django.template.loader import render_to_string

register = template.Library()

SAFE_TAGS = [
    "a",
    "abbr",
    "acronym",
    "b",
    "blockquote",
    "br",
    "cite",
    "code",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "i",
    "li",
    "ol",
    "p",
    "pre",
    "q",
    "s",
    "strike",
    "strong",
    "sub",
    "sup",
    "ul",
    "img",
]

SAFE_ATTRS = {
    "a": ["href", "title"],
    "img": ["src", "style", "width", "height", "alt"],
}

# LinkifyFilter converts raw URLs in text into links
cleaner = Cleaner(tags=SAFE_TAGS, attributes=SAFE_ATTRS, filters=[LinkifyFilter])


@register.filter
def clean(text):
    return mark_safe(cleaner.clean(text))


@register.filter
def markdown(text):
    return mark_safe(cleaner.clean(convert_markdown(text, extensions=["extra"])))


@register.filter
def raw_markdown(text):
    return convert_markdown(text, extensions=["extra"])


@register.filter
def markdown_srcdoc(text):
    puzzle_iframe = render_to_string(
        "view_puzzle_iframe.html",
        {
            "puzzle": text,
        },
    )
    return escape(puzzle_iframe)
