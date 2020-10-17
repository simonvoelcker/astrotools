import os
import csv  # NGC catalog
import sqlite3  # star catalog


class Catalog:
	def __init__(self, path=os.path.join('catalogs', 'NGC.csv'), name_column='Name', name_prefix='NGC'):
		self._header = None
		self._entries = None
		self.path = path
		self.name_column = name_column
		self.name_prefix = name_prefix

	@property
	def entries(self):
		if self._entries is None:
			self._load_entries()
		return self._entries

	def _load_entries(self):
		self._entries = {}
		with open(self.path) as csvfile:
			reader = csv.reader(csvfile, delimiter=';')
			for index, row in enumerate(reader):
				if index == 0:
					self._header = row
					name_column_index = row.index(self.name_column)
					continue
				name = row[name_column_index]
				if name.startswith(self.name_prefix):
					self.entries[name] = row

	def find_entries(self, prefix):
		entries = []
		for name, entry in self.entries.items():
			if name.startswith(prefix):
				entries.append({key: value for key, value in zip(self._header, entry)})
		return entries

	def get_entry(self, name):
		entry = self.entries.get(name)
		if entry is None:
			return None
		return {key: value for key, value in zip(self._header, entry)}

	def get_stars(self, limit=1000):
		directory = '/home/simon/Hobby/astro/Tycho-2/'
		db_file = os.path.join(directory, 'tycho2.db')
		connection = sqlite3.connect(db_file)
		result = connection.execute(f'''
			SELECT ra, dec, mag FROM stars ORDER BY mag LIMIT {limit}
		''')

		return [
			{
				'ra': row[0],
				'dec': row[1],
				'mag': row[2],
			}
			for row in result
		]
