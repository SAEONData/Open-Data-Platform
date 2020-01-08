from .admin import SysAdminModelView, CodeField


class InstitutionRegistryModelView(SysAdminModelView):
    """
    InstitutionRegistry model view.
    """
    column_list = ['name', 'code']
    column_default_sort = 'name'

    form_columns = ['name', 'code']
    form_overrides = {
        'code': CodeField
    }
