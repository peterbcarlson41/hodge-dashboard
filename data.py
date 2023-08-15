import pandas as pd

# The Google Sheet Data
sheet_id = "1vVZvQtGuXmNV0adDhYsE1kzQjs6iEcVbmDgQsfEj_HQ"
sheet_name = "audit_inputs"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# Replace these to import different areas of the data
end_index_x = 16
min_completion_percentage = 0.5  # Minimum completion percentage for a row to be considered complete

def get_data():
    df = pd.read_csv(url)

    # Trim data
    df = df.iloc[:, :end_index_x]

    # Filter rows with at least 50% completeness and no "null" value in the "Restaurants" column
    complete_rows = df[(df.apply(row_completion, axis=1) >= min_completion_percentage) & (df['Restaurant'] != "null")]

    return complete_rows

def row_completion(row):
    return sum(row.notnull()) / len(row)

if __name__ == "__main__":
    df = get_data()

    print(df)
