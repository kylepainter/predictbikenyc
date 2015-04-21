from wtforms import StringField, SubmitField, SelectField, TextAreaField, Form
from wtforms.validators import Required
import pandas as pd
import warnings

warnings.simplefilter("ignore", category = FutureWarning)
#manhattan_url = url_for('static', filename = 'dataframes/manhattanstations.file')
manhattanstations = pd.load('./app/static/dataframes/manhattanstations.file')
manhattanvalues = zip(manhattanstations.id.to_dict().values(),manhattanstations.stAddress1.values)
address_list = [{'id':n[0],'address':n[1]} for n in manhattanvalues]
range(0, 24)

class PredictForm(Form):
    hourlist = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5,]

    start = SelectField(label = 'Start', choices=address_list, validators=[Required()])
    end = SelectField(label = 'End', choices=address_list, validators=[Required()])
 #   hour = SelectField(default = 12, choices = range(0,24), validators=[Required()])
    hour = SelectField(choices=zip(hourlist, hourlist), default=12, validators=[Required()])
    startlatlong = StringField(label = 'StartText', validators=[Required()])
    endlatlong = StringField(label = 'EndText', validators=[Required()])
    submit = SubmitField(label = 'Submit', default="Default text",validators=[Required()])
