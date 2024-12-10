# forms.py

from wtforms import Form, StringField, SelectField, validators

class ProteinSearchForm(Form):
    choices = [('Yeast', 'Yeast')]
    select = SelectField('', choices=choices)
    search = StringField('')
