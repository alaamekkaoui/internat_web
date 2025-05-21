# utilities/xlsx_utils.py
import os
import pandas as pd
from flask import send_file

def export_xlsx(data, filename, folder):
    file_path = os.path.join(folder, filename)
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)

def import_xlsx(file):
    df = pd.read_excel(file)
    return df.to_dict(orient='records')
