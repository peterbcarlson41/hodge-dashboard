import pandas as pd

# As of now, data has to be manually exported from sheet into csv format

# Replace these to import different areas of the data
end_index_y = 470
end_index_x = 16

def get_data():
    # If file is updated, change this location to match the updated csv file location
    file = "data.csv"
    df = pd.read_csv(file)

    # Trim data
    df = df.head(end_index_y)
    df = df.iloc[:end_index_y, :end_index_x]

    return df
