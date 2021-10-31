from datetime import date, datetime, timedelta

import click

from icalendar import Calendar, Event


NB_WEEKS = 40


@click.command()
@click.option('--file', default='./exemple.txt', type=click.Path(exists=True))
@click.option('--start', default=None)
@click.option('--end', default=None)
@click.option('--weeks', type=int, default=None)
@click.option('--verbose/-v', default=False)
def run(file, start, end, weeks, verbose):
    """
    1. Analyse les temps de garde à partir d'un fichier d'entrée.
    Par défaut, s'arrête une semaine (7 jours) après la dernière date spécifiée
    et commence à la première date.
    On peut aussi spécifier `start` et `end` ou `weeks` pour restreindre la fenêtre d'analyse
    (format iso 2019-12-31).

    2. Génère un fichier `.ics` avec l'*ensemble* du calendrier venant du fichier, plus
    NB_WEEKS de projection : 1 semaine en alternance à partir du dernier jour spécifié.

    3. Genère un fichier de sortie `.txt` avec une copie du fichier d'entrée plus
    les projections. Ce fichier devrait servir de fichier d'entrée la fois suivante.
    """
    _calendar = []

    if end and weeks:
        raise click.UsageError('Incompatible options: --end and --weeks')

    # 1. Analyse les temps de garde

    with open(file) as ifile:
        lines = ifile.readlines()
        start_d, start_p = lines[0].split()
        end_d, end_p = lines[-1].split()

        p_file_end_d = date.fromisoformat(end_d)
        p_end_d = p_file_end_d + timedelta(days=6)
        p_start_d = current_d = date.fromisoformat(start_d)
        current_idx = 0
        current_p = start_p

        while(current_d <= p_end_d):
            # switch to next period if neeeded
            # is the current date the one in the next line of the file?
            if current_d <= p_file_end_d and current_d == date.fromisoformat(lines[current_idx + 1].split()[0]):
                current_idx += 1
                new_p = lines[current_idx].split()[1]
                if new_p == current_p:
                    raise Exception('Wrong file format? Person is not changing at %s.' % current_d)
                current_p = new_p
            _calendar.append((current_d, current_p))
            current_d += timedelta(days=1)

    # apply start and end if needed
    calendar = []
    p_start = date.fromisoformat(start) if start else p_start_d
    if weeks:
        p_end = p_start + timedelta(weeks=weeks)
    else:
        p_end = date.fromisoformat(end) if end else None
    for item in _calendar:
        day = item[0]
        if (start and day >= p_start) or not start:
            if not p_end or day <= p_end:
                calendar.append(item)

    print('From %s to %s:' % (p_start, p_end))
    print('-' * 30)
    for p in ['A', 'S']:
        print('%s   %s' % (p, len([c for c in calendar if c[1] == p])))

    if verbose:
        print('-' * 30)
        for item in calendar:
            print('%s   %s' % item)

    # 2. generate .ics

    # we use the unfilterd calendar (_calendar) and
    # keep on iterating on NB_WEEKS on a weekly basis for prediction
    last_line = _calendar[-1]
    next_p = 'A' if last_line[1] == 'S' else 'S'
    last_date = last_line[0]
    for _ in range(NB_WEEKS - 1):
        for d in range(7):
            last_date += timedelta(days=1)
            _calendar.append((last_date, next_p))
        next_p = 'A' if next_p == 'S' else 'S'

    for c_type in ['all', 'A', 'S']:
        cal = Calendar()
        cal.add('prodid', '-//Garde Valentin (%s)//bulte.net//' % c_type)
        cal.add('version', '2.0')
        cal.add('last-modified', datetime.now())

        current_p = None
        previous_event = None
        for (day, p) in _calendar:
            if not current_p or current_p != p:
                current_p = p
                if current_p == c_type or c_type == 'all':
                    event = Event()
                    event.add('uid', f'{day}@bulte.net')
                    event.add('summary', current_p)
                    event.add('dtstart', day)
                    if c_type != 'all':
                        previous_event = None
                if previous_event:
                    previous_event.add('dtend', day)
                    cal.add_component(previous_event)
                previous_event = event
            if (day, p) == _calendar[-1]:
                previous_event.add('dtend', day + timedelta(days=1))
                cal.add_component(previous_event)

        with open('calendar/garde-%s.ics' % c_type, 'wb') as ofile:
            ofile.write(cal.to_ical())

    # 3. generate output file w/ predictions

    output_lines = []
    current_p = None
    for (day, p) in _calendar:
        if not current_p or current_p != p:
            output_lines.append('%s\t%s\n' % (day, p))
            current_p = p
    output_file = './output/%s.txt' % date.today().isoformat()
    with open(output_file, 'w') as ofile:
        ofile.writelines(output_lines)


if __name__ == '__main__':
    run()
