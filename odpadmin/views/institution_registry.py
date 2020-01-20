from .base import SysAdminModelView, KeyField


class InstitutionRegistryModelView(SysAdminModelView):
    """
    InstitutionRegistry model view.
    """
    column_list = ['name', 'key']
    column_default_sort = 'name'

    form_columns = ['name', 'key']
    form_overrides = {
        'key': KeyField
    }
