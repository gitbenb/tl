from natural.constant import _, _multi
import datetime


# Wed, 02 Oct 2002 08:00:00 EST
# Wed, 02 Oct 2002 13:00:00 GMT
# Wed, 02 Oct 2002 15:00:00 +0200
RFC2822_DATETIME_FORMAT = '%a, %d %b %Y %T %z'
# Wed, 02 Oct 02 08:00:00 EST
# Wed, 02 Oct 02 13:00:00 GMT
# Wed, 02 Oct 02 15:00:00 +0200
RFC822_DATETIME_FORMAT  = '%a, %d %b %y %T %z'
# 2012-06-13T15:24:17
ISO8601_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
# Wed, 02 Oct 2002
RFC2822_DATE_FORMAT     = '%a, %d %b %Y'
# Wed, 02 Oct 02
RFC2822_DATE_FORMAT     = '%a, %d %b %y'
# 2012-06-13
ISO8601_DATE_FORMAT     = '%Y-%m-%d'


def _to_datetime(t):
    '''
    Internal function that tries whatever to convert ``t`` into a
    :class:`datetime.datetime` object.
    '''

    if isinstance(t, float) or \
        isinstance(t, int) or \
        isinstance(t, int):
        return datetime.datetime.fromtimestamp(float(t))

    elif isinstance(t, str):
        for format in (
            RFC2822_DATETIME_FORMAT,
            RFC822_DATETIME_FORMAT,
            ISO8601_DATETIME_FORMAT,
            ):
            try:
                return datetime.datetime.strptime(t, format)
            except ValueError:
                pass

        raise ValueError('Format not supported')

    elif isinstance(t, datetime.datetime):
        return t

    elif isinstance(t, datetime.date):
        return datetime.datetime.combine(t, datetime.time(0, 0))

    else:
        raise TypeError


def _to_date(t):
    '''
    Internal function that tries whatever to convert ``t`` into a
    :class:`datetime.date` object.
    '''

    if isinstance(t, float) or \
        isinstance(t, int) or \
        isinstance(t, int):
        return datetime.date.fromtimestamp(float(t))

    elif isinstance(t, str):
        for format in (
            RFC2822_DATE_FORMAT,
            RFC822_DATE_FORMAT,
            ISO8601_DATE_FORMAT,
            ):
            try:
                return datetime.datetime.strptime(t, format).date()
            except ValueError:
                pass

        raise ValueError('Format not supported')

    elif isinstance(t, datetime.datetime):
        return t.date()

    elif isinstance(t, datetime.date):
        return t

    else:
        raise TypeError


def delta(t1, t2, words=True):
    '''
    Calculates the estimated delta between two time objects in human-readable
    format. Used internally by the :func:`day` and :func:`duration` functions.

    :param t1: timestamp, :class:`datetime.date` or :class:`datetime.datetime`
               object
    :param t2: timestamp, :class:`datetime.date` or :class:`datetime.datetime`
               object
    '''

    t1 = _to_datetime(t1)
    t2 = _to_datetime(t2)
    diff = t1 - t2

    if diff.days == 0:
        if diff.seconds < 10 and words:
            return (
                _('just now'),
                0,
            )

        elif diff.seconds < 60:
            return (
                _multi(
                    _('%d second'),
                    _('%d seconds'),
                diff.seconds) % (diff.seconds,),
                0,
            )
        elif diff.seconds < 120 and words:
            return (
                _('a minute'),
                0,
            )

        elif diff.seconds < 3600:
            minutes, seconds = divmod(diff.seconds, 60)
            return (
                _multi(
                    _('%d minute'),
                    _('%d minutes'),
                minutes) % (minutes,),
                seconds,
            )
        elif diff.seconds < 7200 and words:
            return (
                _('an hour'),
                0,
            )

        elif diff.seconds < 86400:
            hours, seconds = divmod(diff.seconds, 3600)
            return (
                _multi(
                    _('%d hour'),
                    _('%d hours'),
                hours) % (hours,),
                seconds,
            )

    elif diff.days == 1 and words:
        return (
            _('yesterday'),
            0,
        )

    elif diff.days < 7:
        return (
            _multi(
                _('%d day'),
                _('%d days'),
            diff.days) % (diff.days,),
            diff.seconds,
        )

    elif diff.days < 31:
        weeks, days = divmod(diff.days, 7)
        seconds = days * 86400 + diff.seconds
        return (
            _multi(
                _('%d week'),
                _('%d weeks'),
            weeks) % (weeks,),
            seconds,
        )

    elif diff.days < 365:
        months, days = divmod(diff.days, 30)
        seconds = days * 86400 + diff.seconds
        return (
            _multi(
                _('%d month'),
                _('%d months'),
            months) % (months,),
            seconds,
        )

    else:
        years, days = divmod(diff.days, 365)
        seconds = days * 86400 + diff.seconds
        return (
            _multi(
                _('%d year'),
                _('%d years'),
            years) % (years,),
            seconds,
        )


def day(t, now=None, format='%B %d'):
    '''
    Date delta compared to ``t``. You can override ``now`` to specify what date
    to compare to.

    You can override the date format by supplying a ``format`` parameter.

    :param t: timestamp, :class:`datetime.date` or :class:`datetime.datetime`
              object
    :param now: default ``None``, optionally a :class:`datetime.datetime`
                object
    :param format: default ``'%B %d'``
    '''
    t1 = _to_date(t)
    t2 = _to_date(now or datetime.datetime.now())
    diff = max(t1, t2) - min(t1, t2)

    if diff.days == 0:
        return _('today')
    elif diff.days == 1:
        if t1 < t2:
            return _('yesterday')
        else:
            return _('tomorrow')
    elif diff.days == 7:
        if t1 < t2:
            return _('last week')
        else:
            return _('next week')
    else:
        return t1.strftime(format)


def duration(t, now=None, precision=1, pad=', ', words=None, plain=False):
    '''
    Time delta compared to ``t``. You can override ``now`` to specify what time
    to compare to.

    :param t: timestamp, :class:`datetime.date` or :class:`datetime.datetime`
              object
    :param now: default ``None``, optionally a :class:`datetime.datetime`
                object
    :param precision: default ``1``, number of fragments to return
    :param words: default ``None``, allow words like "yesterday", if set to
                  ``None`` this will be enabled if ``precision`` is set to
                  ``1``
    '''

    if words is None:
        words = precision == 1

    t1 = _to_datetime(t)
    t2 = _to_datetime(now or datetime.datetime.now())

    if not plain:
        if t1 < t2:
            format = _('%s ago')
        else:
            format = _('%s from now')
    else: format = _('%s')

    result, remains = delta(max(t1, t2), min(t1, t2), words=words)
    if result in (_('just now'), _('yesterday')):
        return result
    elif precision > 1 and remains:
        t3 = t2 - datetime.timedelta(seconds=remains)
        return pad.join([
            result,
            duration(t3, t2, precision - 1, pad, words=False),
        ])
    else:
        return format % (result,)


def compress(t, sign=False, pad=''):
    '''
    Convert the input to compressed format, works with a
    :class:`datetime.timedelta` object or a number that represents the number
    of seconds you want to compress.  If you supply a timestamp or a
    :class:`datetime.datetime` object, it will give the delta relative to the
    current time.

    You can enable showing a sign in front of the compressed format with the
    ``sign`` parameter, the default is not to show signs.

    Optionally, you can chose to pad the output. If you wish your values to be
    separated by spaces, set ``pad`` to ``' '``.

    :param t: seconds or :class:`datetime.timedelta` object
    :param sign: default ``False``
    :param pad: default ``u''``
    '''

    if isinstance(t, datetime.timedelta):
        seconds = t.seconds + (t.days * 86400)
    elif isinstance(t, float) or isinstance(t, int) or isinstance(t, int):
        seconds = int(t)
    else:
        return compress(datetime.datetime.now() - _to_datetime(t), sign, pad)

    parts = []
    if sign:
        parts.append('-' if d.days < 0 else '+')

    weeks, seconds   = divmod(seconds, 604800)
    days, seconds    = divmod(seconds, 86400)
    hours, seconds   = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    if weeks:
        parts.append(_('%dw') % (weeks,))
    if days:
        parts.append(_('%dd') % (days,))
    if hours:
        parts.append(_('%dh') % (hours,))
    if minutes:
        parts.append(_('%dm') % (minutes,))
    if seconds:
        parts.append(_('%ds') % (seconds,))

    return pad.join(parts)
