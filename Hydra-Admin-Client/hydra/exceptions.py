class HydraAdminError(Exception):
    def __init__(self, *args, **kwargs):
        self.method = kwargs.pop('method')
        self.endpoint = kwargs.pop('endpoint')
        self.status_code = kwargs.pop('status_code')
        self.error_detail = kwargs.pop('error_detail', str(args))
