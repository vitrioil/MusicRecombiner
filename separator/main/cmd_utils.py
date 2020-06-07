import itertools
import uuid

# package import
from separator import db
from separator.models import Volume, Copy, Overlay


def store_volume_attr(from_json, sample_rate, augment, *args, **kwargs):
    def _retrieve_from_json(params, cmd_id, audio_name):
        for param in params:
            start = float(param.get("start"))
            end = float(param.get("end"))
            vol = int(param.get("volume", 100)) / 100
            if vol == 1:
                continue
            volume = Volume(vol_id=uuid.uuid4(), cmd_id=cmd_id,
                            start=start, end=end, volume=vol,
                            stem_name=audio_name)
            db.session.add(volume)
            yield start, end, vol

    def _retrieve_from_db(volume_list):
        for volume in volume_list:
            start = volume.start
            end = volume.end
            vol = volume.volume

            yield start, end, vol

    _retrieve = _retrieve_from_json if from_json else _retrieve_from_db
    for start, end, vol in _retrieve(*args, **kwargs):
        augment = augment.amplitude(interval=(start, end), gain=vol,
                                    sample_rate=sample_rate)
    return augment

def store_copy_attr(from_json, sample_rate, augment, *args, **kwargs):
    def _retrieve_from_json(params, cmd_id, audio_name):
        for param in params:
            start = float(param.get("start"))
            end = float(param.get("end"))
            copy_start = float(param.get("copyStart"))

            copy = Copy(copy_id=uuid.uuid4(), cmd_id=cmd_id,
                        start=start, end=end, copy_start=copy_start,
                        stem_name=audio_name)
            db.session.add(copy)
            yield start, end, copy_start

    def _retrieve_from_db(copy_list):
        for copy in copy_list:
            start = copy.start
            end = copy.end
            copy_start = copy.copy_start
            yield start, end, copy_start

    _retrieve = _retrieve_from_json if from_json else _retrieve_from_db
    for start, end, copy_start in _retrieve(*args, **kwargs):
        augment = augment.copy(interval=(start, end), copy_start=copy_start,
                               sample_rate=sample_rate)
    return augment

def store_overlay_attr(from_json, sample_rate, augment, *args, **kwargs):
    def _retrieve_from_json(params, cmd_id, audio_name):
        for param in params:
            start = float(param.get("start"))
            end = float(param.get("end"))
            overlay_start = float(param.get("overlayStart"))

            overlay = Overlay(overlay_id=uuid.uuid4(), cmd_id=cmd_id,
                              start=start, end=end, overlay_start=overlay_start,
                              stem_name=audio_name)
            db.session.add(overlay)
            yield start, end, overlay_start

    def _retrieve_from_db(overlay_list):
        for overlay in overlay_list:
            start = overlay.start
            end = overlay.end
            overlay_start = overlay.overlay_start
            yield start, end, overlay_start

    _retrieve = _retrieve_from_json if from_json else _retrieve_from_db
    for start, end, overlay_start in _retrieve(*args, **kwargs):
        augment = augment.overlay(interval=(start, end), overlay_start=overlay_start,
                                  sample_rate=sample_rate)
    return augment

def get_command_list(command_ids, stem_name):

    volume_list = [Volume.query.filter_by(cmd_id=c, stem_name=stem_name).all() for c in command_ids]
    volume_list = itertools.chain.from_iterable(volume_list)

    copy_list = [Copy.query.filter_by(cmd_id=c, stem_name=stem_name).all() for c in command_ids]
    copy_list = itertools.chain.from_iterable(copy_list)

    overlay_list = [Overlay.query.filter_by(cmd_id=c, stem_name=stem_name).all() for c in command_ids]
    overlay_list = itertools.chain.from_iterable(overlay_list)

    commands = {"Volume": volume_list, "Copy": copy_list, "Overlay": overlay_list}
    return commands

# MAP Command to function
CMD_MAP = {"Volume": store_volume_attr, "Copy": store_copy_attr, "Overlay": store_overlay_attr}
