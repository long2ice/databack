import os

import i18n
from i18n import load_path

from databack.constants import BASE_DIR


def init():
    load_path.append(os.path.join(BASE_DIR, "databack", "locales"))
    i18n.set("enable_memoization", True)
    i18n.set("fallback", "en-US")
    i18n.set("skip_locale_root_data", True)
    i18n.set("filename_format", "{locale}.{format}")
