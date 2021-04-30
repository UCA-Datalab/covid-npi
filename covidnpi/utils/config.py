import toml


def load_config(path: str, key: str = None):
    """Load TOML config as dict
    Parameters
    ----------
    path : str
        Path to TOML config file
    key : str, optional
        Section of the conf file to load
    Returns
    -------
    dict
        Config dictionary
    """
    try:
        config = toml.load(path)
        return config if key is None else config[key]
    except:
        raise ValueError(f"Path to config not found: {path}")
