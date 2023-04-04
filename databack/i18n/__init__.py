import os
import i18n

from databack.constants import BASE_DIR


def init():
    i18n.load_path.append(os.path.join(BASE_DIR, "databack", "i18n"))
    i18n.set("enable_memoization", True)
    i18n.set("fallback", "en-US")
    i18n.set("skip_locale_root_data", True)
    i18n.set("filename_format", "{locale}.{format}")
