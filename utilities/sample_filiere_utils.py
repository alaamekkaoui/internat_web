import io
import pandas as pd
from flask import send_file

def generate_sample_filieres_xlsx():
    data = [
        {'name': 'Informatique'},
        {'name': 'Agronomie'},
        {'name': 'Génie Rural'},
    ]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name='sample_filieres.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
