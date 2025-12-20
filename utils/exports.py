import csv
import io
from openpyxl import Workbook
from django.http import HttpResponse


def export_to_csv(data):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="leads.csv"'
    return response


def export_to_excel(data):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Leads"
    sheet.append(list(data[0].keys()))
    for row in data:
        sheet.append(list(row.values()))
    output = io.BytesIO()
    workbook.save(output)
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="leads.xlsx"'
    return response
