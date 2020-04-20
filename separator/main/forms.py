from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import SubmitField, RadioField
from wtforms.validators import DataRequired


class UploadForm(FlaskForm):
    audio = FileField("Audio File", validators=[DataRequired(), FileAllowed(["mp3"])])
    stems = RadioField("Stems", choices=[(2, "Vocals/Accompaniment"), (4, "Vocal/Drum/Bass/Other"), (5, "Vocal/Drum/Bass/Piano/Other")])
    submit = SubmitField("Upload")

