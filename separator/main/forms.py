from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import SubmitField, RadioField
from wtforms.validators import DataRequired


class UploadForm(FlaskForm):
    audio = FileField("Audio File", validators=[DataRequired()])
    stems = RadioField("Stems", choices=[(2, "Vocals/Accompaniment"), (4, "Vocal/Drum/Bass/Other"), (5, "Vocal/Drum/Bass/Piano/Other")], coerce=int)
    submit = SubmitField("Upload")

class AugmentForm(FlaskForm):
    augment = RadioField("Augment", choices=[(0, "Volume"), (1, "Copy")], coerce=int)
