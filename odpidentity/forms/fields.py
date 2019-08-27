from wtforms import SelectMultipleField


class DualListboxField(SelectMultipleField):
    """
    Custom field that works with a dual listbox component, useful for managing
    many-to-many relations.
    """

    def __init__(self, model_class, model_pk='id', **kwargs):
        """
        Constructor.

        :param model_class: the SQLAlchemy model for the objects that populate this field
        :param model_pk: the primary key column of the model; default: 'id'
        :param kwargs: additional keyword args passed to the inherited field constructor
        """
        kwargs.pop('allow_blank', None)
        super().__init__(**kwargs)
        if callable(self.choices):
            self.choices = self.choices()
        self.model_class = model_class
        self.model_pk = model_pk
        self.coerce = self._coerce

    def _coerce(self, value):
        if type(value) is self.model_class:
            return value
        return self.model_class.query.get(value)

    def pre_validate(self, form):
        if self.data:
            values = list(c[0] for c in self.choices)
            for d in self.data:
                if getattr(d, self.model_pk) not in values:
                    raise ValueError(self.gettext("'%(value)s' is not a valid choice for this field") % dict(value=d))
