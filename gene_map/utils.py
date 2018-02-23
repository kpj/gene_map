from appdirs import AppDirs


def get_data_directory() -> str:
    adirs = AppDirs('gene_map', 'kpj')
    return adirs.user_data_dir
