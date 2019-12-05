from datetime import date, timedelta
import click


@click.command()
@click.option('--file', default='./exemple.txt', type=click.Path(exists=True))
@click.option('--start', default=None)
@click.option('--end', default=None)
@click.option('--weeks', type=int, default=None)
@click.option('--verbose/-v', default=False)
def run(file, start, end, weeks, verbose):
    """
    Analyse les temps de garde à partir d'un fichier d'entrée.
    Par défaut, s'arrête une semaine (7 jours) après la dernière date spécifiée.
    """
    _calendar = []

    if end and weeks:
        raise Exception('Incompatible options: --end and --weeks')

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
            if (end and day <= p_end) or not end:
                calendar.append(item)

    print('From %s to %s:' % (p_start, p_end))
    print('-' * 30)
    for p in ['A', 'S']:
        print('%s   %s' % (p, len([c for c in calendar if c[1] == p])))

    if verbose:
        print('-' * 30)
        for item in calendar:
            print('%s   %s' % item)

if __name__ == '__main__':
    run()
