import io
import pandas as pd
from flask import send_file

def generate_sample_rooms_xlsx():
    data = [
        {'room_number': '101', 'pavilion': 'A', 'room_type': 'single'},
        {'room_number': '102', 'pavilion': 'B', 'room_type': 'double'},
        {'room_number': '103', 'pavilion': 'C', 'room_type': 'triple'},
    ]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name='sample_rooms.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
