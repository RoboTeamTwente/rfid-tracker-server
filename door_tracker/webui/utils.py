import csv

from django.http import HttpResponse


def logs_to_csv(logs):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response, dialect='excel')
    writer.writerow(['time', 'type', 'tag', 'owner_first', 'owner_last', 'scanner'])
    for log in logs:
        tag_name = '-'
        tag_owner_first = '-'
        tag_owner_last = '-'
        scanner_name = 'WebUI'
        if log.tag:
            tag_name = log.tag.name or '-'
            if log.tag.owner:
                tag_owner_first = log.tag.owner.first_name
                tag_owner_last = log.tag.owner.last_name
        if log.scanner:
            scanner_name = log.scanner.name
        writer.writerow(
            [
                log.time.strftime('%F %T'),
                log.type,
                tag_name,
                tag_owner_first,
                tag_owner_last,
                scanner_name,
            ]
        )
    return response
