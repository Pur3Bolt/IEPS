from .common import GenericTable


class SiteTable(GenericTable):
    table = 'site'


class PageTable(GenericTable):
    table = 'page'


class LinkTable(GenericTable):
    table = 'link'


class ImageTable(GenericTable):
    table = 'image'


class PageDataTable(GenericTable):
    table = 'page_data'


class PageTypeTable(GenericTable):
    table = 'page_type'


class DataTypeTable(GenericTable):
    table = 'data_type'


class SiteIPAddrTable(GenericTable):
    table = 'site_ipaddr'
