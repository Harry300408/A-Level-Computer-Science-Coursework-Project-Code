import configparser
import json
import os


DEFAULTS_FILE = "defaults.json"
SETTINGS_FILE = "settings.ini"


def _load_defaults():
    try:
        with open(DEFAULTS_FILE, "r", encoding="utf-8") as default_file:
            raw_defaults = json.load(default_file)
    except Exception as exc:
        raise SystemError(
            "'defaults.json' file not found or doesn't have the right values, "
            "please either repair the game or redownload from source."
        ) from exc

    window_defaults = raw_defaults["window_setup_defaults"]
    audio_defaults = raw_defaults.get("audio_defaults", {})
    default_settings = {
        "xres": window_defaults["xresolution"],
        "yres": window_defaults["yresolution"],
        "fullscreen": window_defaults["fullscreen"],
        "fps": window_defaults["fps"],
        "language": raw_defaults["language"],
        "music_volume": audio_defaults.get("music_volume", 100),
        "sfx_volume": audio_defaults.get("sfx_volume", 100),
    }

    return _normalize_settings(default_settings, default_settings)


def _to_bool(value):
    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _clamp_int(value, minimum, maximum, fallback):
    try:
        value = int(float(value))
    except (TypeError, ValueError):
        value = fallback

    return max(minimum, min(maximum, value))


def _normalize_settings(settings, base_settings):
    merged_settings = base_settings.copy()

    if settings is not None:
        merged_settings.update(settings)

    merged_settings["xres"] = _clamp_int(
        merged_settings.get("xres"),
        320,
        7680,
        base_settings["xres"],
    )
    merged_settings["yres"] = _clamp_int(
        merged_settings.get("yres"),
        240,
        4320,
        base_settings["yres"],
    )
    merged_settings["fullscreen"] = _to_bool(
        merged_settings.get("fullscreen", base_settings["fullscreen"])
    )
    merged_settings["fps"] = _clamp_int(
        merged_settings.get("fps"),
        1,
        240,
        base_settings["fps"],
    )
    merged_settings["language"] = str(
        merged_settings.get("language", base_settings["language"])
    ).strip() or base_settings["language"]
    merged_settings["music_volume"] = _clamp_int(
        merged_settings.get("music_volume"),
        0,
        100,
        base_settings["music_volume"],
    )
    merged_settings["sfx_volume"] = _clamp_int(
        merged_settings.get("sfx_volume"),
        0,
        100,
        base_settings["sfx_volume"],
    )

    return merged_settings


def normalize_settings(settings, defaults=None):
    base_settings = _load_defaults() if defaults is None else defaults.copy()
    return _normalize_settings(settings, base_settings)


def _build_config(settings):
    config = configparser.ConfigParser()

    config["RESOLUTION"] = {
        "xres": str(settings["xres"]),
        "yres": str(settings["yres"]),
    }
    config["SCREEN"] = {
        "fullscreen": str(settings["fullscreen"]),
        "fps": str(settings["fps"]),
    }
    config["LANGUAGE"] = {
        "locale": str(settings["language"]),
    }
    config["AUDIO"] = {
        "music_volume": str(settings["music_volume"]),
        "sfx_volume": str(settings["sfx_volume"]),
    }

    return config


def save_settings(settings):
    normalized_settings = normalize_settings(settings)
    config = _build_config(normalized_settings)

    with open(SETTINGS_FILE, "w", encoding="utf-8") as config_file:
        config.write(config_file)

    return normalized_settings


def load_settings():
    defaults = _load_defaults()

    if not os.path.exists(SETTINGS_FILE):
        print(f"[ENGINE] Settings file '{SETTINGS_FILE}' not found. Creating new settings file with default values...")
        return save_settings(defaults)

    print(f"[ENGINE] Settings file found. Loading settings from '{SETTINGS_FILE}'...")

    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE)

    loaded_settings = defaults.copy()
    file_was_incomplete = False

    try:
        loaded_settings["xres"] = config.getint("RESOLUTION", "xres")
        print(f"[ENGINE] Loaded xres: {loaded_settings['xres']}")
    except (configparser.Error, TypeError, ValueError):
        file_was_incomplete = True

    try:
        loaded_settings["yres"] = config.getint("RESOLUTION", "yres")
        print(f"[ENGINE] Loaded yres: {loaded_settings['yres']}")
    except (configparser.Error, TypeError, ValueError):
        file_was_incomplete = True

    try:
        loaded_settings["fullscreen"] = config.getboolean("SCREEN", "fullscreen")
        print(f"[ENGINE] Loaded fullscreen: {loaded_settings['fullscreen']}")
    except (configparser.Error, TypeError, ValueError):
        file_was_incomplete = True

    try:
        loaded_settings["fps"] = config.getint("SCREEN", "fps")
        print(f"[ENGINE] Loaded fps: {loaded_settings['fps']}")
    except (configparser.Error, TypeError, ValueError):
        file_was_incomplete = True

    try:
        loaded_settings["language"] = config.get("LANGUAGE", "locale")
        print(f"[ENGINE] Loaded language: {loaded_settings['language']}")
    except (configparser.Error, TypeError, ValueError):
        file_was_incomplete = True

    try:
        loaded_settings["music_volume"] = config.getint("AUDIO", "music_volume")
        print(f"[ENGINE] Loaded music_volume: {loaded_settings['music_volume']}")
    except (configparser.Error, TypeError, ValueError):
        file_was_incomplete = True

    try:
        loaded_settings["sfx_volume"] = config.getint("AUDIO", "sfx_volume")
        print(f"[ENGINE] Loaded sfx_volume: {loaded_settings['sfx_volume']}")
    except (configparser.Error, TypeError, ValueError):
        file_was_incomplete = True

    normalized_settings = normalize_settings(loaded_settings, defaults=defaults)

    if file_was_incomplete or normalized_settings != loaded_settings:
        return save_settings(normalized_settings)

    return normalized_settings


def settings_to_window_configs(settings):
    return [
        settings["xres"],
        settings["yres"],
        settings["fullscreen"],
        settings["fps"],
    ]


def window_configs_setup():
    return settings_to_window_configs(load_settings())


def set_window_configs_to_default():
    default_settings = _load_defaults()
    save_settings(default_settings)
    return settings_to_window_configs(default_settings)


def game_lang_load():
    return str(load_settings()["language"])
