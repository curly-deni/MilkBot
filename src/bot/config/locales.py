__all__ = [
    "LOCALES_DICT",
    "LIB_LOCALES",
    "APP_LOCALES",
    "DEFAULT_LOCALE",
    "RESQUE_LOCALE",
    "ORIGINAL_LOCALE",
]

# translate locale to locale file
LOCALES_DICT = {
    "da": "da",
    "de": "de",
    "en-GB": "en",
    "en-US": "en",
    "es-ES": "es",
    "fr": "fr",
    "hr": "hr",
    "id": "id",
    "it": "it",
    "nl": "nl",
    "no": "no",
    "pl": "pl",
    "cs": "cs",
    "bg": "bg",
    "uk": "uk",
    "th": "th",
    "zh-CN": "zh",
    "ja": "ja",
    "zh-TW": "zh",
    "ko": "ko",
}

# locale files
LIB_LOCALES = ["en", "ru"]
APP_LOCALES = ["ru"]

# used to generate locale files
ORIGINAL_LOCALE = "ru"

# used by default when no locale is specified
DEFAULT_LOCALE = "en"

# used when default locale is broken
RESQUE_LOCALE = "ru"
