import pandas as pd

#The Google Sheet Data
sheet_id = "1vVZvQtGuXmNV0adDhYsE1kzQjs6iEcVbmDgQsfEj_HQ"
sheet_name = "audit_inputs"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# Replace these to import different areas of the data
end_index_y = 470
end_index_x = 16

def get_data():
    df = pd.read_csv(url)

    # Trim data
    df = df.head(end_index_y)
    df = df.iloc[:end_index_y, :end_index_x]

    return df

if __name__ == "__main__":
    df = get_data()
    print(df)
