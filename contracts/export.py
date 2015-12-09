# coding=utf-8
from django.conf import settings
from django.utils import formats, dateformat
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from utils import load_estimated_hours, load_spent_hours
from unicodecsv import UnicodeWriter

import datetime
import StringIO

styleSheet = getSampleStyleSheet()


def datetime_format(value):
    fmt = formats.get_format("DATETIME_FORMAT", lang=settings.LANGUAGE_CODE)
    return dateformat.format(value, fmt)


def date_format(value):
    fmt = formats.get_format("DATE_FORMAT", lang=settings.LANGUAGE_CODE)
    return dateformat.format(value, fmt)


def get_filename(company, fmt):
    dtstr = datetime.date.today().strftime('%d-%m-%Y')
    return "{0}_{1!s}.{2!s}".format(company, dtstr, fmt)


def make_rows(contract, tickets):

    headers = [
        'subject',
        lambda c, o: datetime_format(o.updated_at),
        load_spent_hours,
        load_estimated_hours
    ]
    rows = []
    for obj in tickets:
        row = []
        for header in headers:
            if callable(header):
                row.append(header(contract, obj))
            else:
                row.append(getattr(obj, header))
        rows.append(row)

    return rows


def make_tables(store, rows):
    table = Table(rows, colWidths=[500, 100, 70, 85])
    table.setStyle(
        TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.gray),
            ('GRID', (0, 0), (-1, 0), 0.25, colors.blue),
            ('ALIGN', (1, 0), (-1, len(rows) - 1), 'CENTER')
        ]))

    store.append(table)
    store.append(Spacer(1, 0.5 * inch))

    return table


def report_as_pdf(contract, intervals, spent_hours, remainder_hours):

    """
    Gera o pdf do relatório

    :param contract:
    :param intervals:
    :param spent_hours:
    :param remainder_hours:
    :return:
    """
    company_name = contract.company.name

    buff = StringIO.StringIO()
    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(buff, pagesize=landscape(A4), title='Relatório de horas')

    # Adiciona nome da empresa ao pdf
    store = [Paragraph('<para align=center spaceb=3>RELATÓRIO DE HORAS - '+company_name+'</para>',
                       styleSheet["h3"]),
             Spacer(1, 0.5 * inch)]

    # Tabelas por período
    for period in intervals:
        # Adicionando periodo ao pdf
        if len(intervals[period]) != 0:
            store.append(Paragraph('<para align=center spaceb=3>'+str(period)+'</para>', styleSheet["h4"]))
            rows = [settings.EXPORT_CSV_COLUMNS]
            rows.extend(make_rows(contract, intervals[period]))
            make_tables(store, rows)
            del rows[:]

    resume = Table([
        ['Total de horas', 'Horas gastas', 'Horas restantes'],
        [contract.hours, spent_hours, remainder_hours]
    ])
    resume.setStyle(
        TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.gray),
            ('LINEBELOW', (0, 0), (-1, 0), 0.20, colors.blue),
            ('ALIGN', (0, 0), (-1, 1), 'CENTER')
        ]))
    store.append(resume)
    doc.build(store)
    pdf = buff.getvalue()
    buff.close()

    return pdf


def report_as_csv(contract, intervals, spent_hours, remainder_hours):
    """
    Gera o csv do relatório

    :param contract:
    :param intervals:
    :param spent_hours:
    :param remainder_hours:
    :return:
    """
    stream = StringIO.StringIO()
    csv_writer = UnicodeWriter(stream)
    # Adiciona nome da empresa ao csv
    company_name = contract.company.name
    csv_writer.writerow([u'RELATÓRIO DE HORAS - '+company_name])

    # Adicionando periodo ao csv, se selecionado
    for period in intervals:
        if len(intervals[period]) != 0:
            csv_writer.writerow([str(period)])
            csv_writer.writerow(settings.EXPORT_CSV_COLUMNS)
            csv_writer.writerows(make_rows(contract, intervals[period]))

    csv_writer.writerows([
        ['Total de horas', 'Horas gastas', 'Horas restantes'],
        [contract.hours, spent_hours, remainder_hours]
    ])
    csv_file = stream.getvalue()
    stream.close()

    return csv_file
