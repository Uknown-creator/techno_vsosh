from git import Repo


def get_hash():
    try:
        hash_ = Repo().head.commit.hexsha
        return f'<a href="https://github.com/Uknown-creator/techno_vsosh/commit/{hash_}">GitHub</a>'
    except Exception:
        return '<a href="https://github.com/Uknown-creator/techno_vsosh">GitHub</a>'
