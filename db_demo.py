from pa1.database.tables import SiteTable, ImageTable

site = SiteTable()
print(site.read_from_site())

image = ImageTable()
print(image.read_from_site())
