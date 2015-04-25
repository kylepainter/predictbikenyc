import pandas as pd
import warnings
warnings.simplefilter("ignore", category = FutureWarning) # eliminates pandas future warning for pickled df


project_location = '/home/vagrant/projectcode/predictbikenyc'
path_for_df = project_location + '/app/static/dataframes/'

# manstations.csv is derived from citibike api, filtered for Manhattan-only stations,
# and coded according to zone.

# opens csv for manhattanstations, alter for use in merges, save df
manhattanstations = pd.read_csv(path_for_df + 'manstations.csv')
manhattanstations = manhattanstations.set_index('index')
manhattanstations = manhattanstations.sort()
manhattanstations['id'] = manhattanstations.id.astype(str)
manhattanstations.save(path_for_df + 'manhattanstations.file')