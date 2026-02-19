from os import cpu_count
from uuid import uuid4


def get_threads_count() -> int:
    return min(6, max(1, (cpu_count() or 1) - 2))


def get_source_file_path(instance, filename, folder=None):
    model_name = instance._meta.model_name
    path = f"{folder}/{filename}" if folder else filename

    if model_name == "movie":
        return f"titles_{instance.id}/{path}"

    if model_name == "episode":
        try:
            title_id = instance.series.id
            s_num = instance.season_number
            e_num = instance.episode_number
            return f"titles_{title_id}/season_{s_num}/ep_{e_num}/{path}"
        except AttributeError:
            pass

    return f"uploads/misc/{uuid4()}/{filename}"
