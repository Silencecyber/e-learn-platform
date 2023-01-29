# This is a script that helps to prevent XSS attacks
import bleach
from bleach.css_sanitizer import CSSSanitizer

BLEACH_VALID_TAGS = (
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'br', 'code',
    'dd', 'div', 'dt', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'hr', 'i', 'img', 'li', 'ol', 'p', 'pre', 'span', 'strike',
    'strong', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th',
    'thead', 'tr', 'tt', 'u', 'ul'
)

BLEACH_VALID_ATTRS = {
    '*': ['style', ],  # allow all tags to have style attr
    'p': ['align', ],
    'a': ['href', 'rel'],
    'img': ['src', 'alt', 'style'],
}

BLEACH_VALID_STYLES = (
    'azimuth', 'background', 'background-color', 'border', 'border-bottom-color',
    'border-collapse', 'border-color', 'border-left-color',
    'border-right-color', 'border-top-color', 'clear',
    'color', 'cursor', 'direction', 'display', 'elevation', 'float',
    'font', 'font-family', 'font-size', 'font-style', 'font-variant',
    'font-weight', 'height', 'letter-spacing', 'line-height',
    'margin', 'margin-bottom', 'margin-left', 'margin-right',
    'margin-top', 'overflow', 'padding', 'padding-bottom',
    'padding-left', 'padding-right', 'padding-top', 'pause',
    'pause-after', 'pause-before', 'pitch', 'pitch-range',
    'richness', 'speak', 'speak-header', 'speak-numeral',
    'speak-punctuation', 'speech-rate', 'stress', 'text-align',
    'text-decoration', 'text-indent', 'unicode-bidi',
    'vertical-align', 'voice-family', 'volume', 'white-space', 'width'
)

BLEACH_VALID_PROTOCOLS = ('https',)

css_sanitizer = CSSSanitizer(allowed_css_properties=BLEACH_VALID_STYLES)


def clean_user_data(data):
    clean_data = bleach.clean(data,
                              tags=BLEACH_VALID_TAGS,
                              attributes=BLEACH_VALID_ATTRS,
                              protocols=BLEACH_VALID_PROTOCOLS,
                              css_sanitizer=css_sanitizer,
                              strip=True,
                              )
    return clean_data
