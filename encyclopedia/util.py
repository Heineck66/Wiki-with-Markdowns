import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename) for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content.encode('utf-8')))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None


def markup(entrydoc):

    newdoc = entrydoc

    # h3
    newdoc = re.sub(r'#{6} ([\w \W][^\n]+)', r'<h6>\1</h6>', newdoc)
    # (([\w\s])(#{6} )){1}([\w ,.]+)

    # h2
    newdoc = re.sub(r'#{2} ([\w \W][^\n]+)', r'<h2>\1</h2>', newdoc)
    # (([\w\s])(#{2} )){1}([\w ,.]+)

    # h1
    newdoc = re.sub(r'# ([\w \W][^\n]+)', r'<h1>\1</h1>', newdoc)

    # quote
    newdoc = re.sub(r'\n>(.+[^\n])', r'<p class="quote">\1</p>', newdoc)
    # (([\w\s])> ){1}([\w \W]+\n)(\n{3})

    # quoteing code
    newdoc = re.sub(r'[`]{3}([\w\W]+)[`]{3}', r'<p class="codequote">\1\n</p>', newdoc)
    # '([\s\w?]{1}[`]{3})([\w\s]+[^_*]+)([`]{3}[\s\W\w]{1})'

    # All bold and italic	*** ***
    newdoc = re.sub(r'[*]{3}([\w\s]+[^_*]+)[*]{3}', r'<em>\1</b></em>', newdoc)
    # '([*]{3})([\w\s]+[^_*]+)([*]{3}[\s]{1})'

    # Bold ** ** or __ __
    newdoc = re.sub(r'[*]{2}([\w\s]+[^\\*\n]+)[*]{2}', r'<b>\1</b>', newdoc)
    newdoc = re.sub(r'[_]{2}([\w\s]+[^\\*\n]+)[_]{2}', r'<b>\1</b>', newdoc)
    # '((([*]{2}|_{2}))([\w\s]+[^_*]+)(([*]{2}|_{2})\s)'

    # Italic * * or _ _
    newdoc = re.sub(r'[*]([^\\_*\n]+.+[^\\_\n]+)[*]', r'<i>\1</i>', newdoc)
    newdoc = re.sub(r'_([\w\s]+[^_*\n]+)_', r'<i>\1</i>', newdoc)
    # '([*]{1})([\w\s]+[^_*]+)([*]{1}[\s]{1})'

    # Strikethrough	~~ ~~
    newdoc = re.sub(r'(~{2})(.+[^\\~\n]+)~{2}', r'<strike>\2</strike>', newdoc)
    # '([~]{2})([\w\s]+[^_*]+)([~]{2}|_{2})\s'

    # get link
    newdoc = re.sub(r'[\[]([\w ]+)[\]][(]([\w/:.]+)[)]', r'<a href="\2">\1</a>', newdoc)
    # [\[]([\w ]+)[\]][(]([\w/:.]+)[)]

    # Get list - or *
    newdoc = re.sub(r'\n[-*] (.+)', r'<li>\1</li>', newdoc)
    # ^- (.+)

    # Get list numerical n.
    newdoc = re.sub(r'(\n\d+[.])(.+)', r'\1 \2', newdoc)

    # new line
    newdoc = re.sub(r'[\n]', r'<br>', newdoc)

    # search for escape caracter
    newdoc = re.sub(r'[\\]([*_>\-#])', r'\1', newdoc)
    # [\\][*_>\-#]

    return newdoc
