from typing import List, Generator, Union, TypeVar
from dateutil.relativedelta import relativedelta

import datetime


def datetime_range(
    date_start: Union[datetime.date, datetime.datetime],
    date_end: Union[datetime.date, datetime.datetime],
    frequency: relativedelta,
    add_first_input_date: bool = True,
    reverse: bool = False
) -> Generator[datetime.date, None, None]:
    """Generator that yields dates that are a fixed time apart, set in the `frequency` parameter, a dateutil.relativedelta.relativedelta object."""

    # datetime.datetime is inherently an instance of datetime.date
    if not isinstance(date_start, datetime.datetime):
        if not isinstance(date_start, datetime.date):
            raise ValueError("date_start mumst be of type datetime.datetime or datetime.date")
        #endif

        # add the time part
        date_start = datetime.datetime.combine(date_start, datetime.time.min)
    #endif

    if not isinstance(date_end, datetime.datetime):
        if not isinstance(date_end, datetime.date):
            raise ValueError("date_end must be of type datetime.datetime or datetime.date")
        #endif

        # add the time part
        date_end = datetime.datetime.combine(date_end, datetime.time.min)
    #endif

    if date_start > date_end:
        raise ValueError(f"starting date must be before the end date")
    #endif

    cycle = 0 if add_first_input_date else 1

    # these two loops are basically the same exept for some comparisons,
    # it is more efficient to compute the main comparison (if reverse) one time than
    # checking it for each cycle
    if reverse:
        while True:
            entry = date_end - (cycle * frequency)

            if entry < date_start:
                break

            cycle += 1
            yield entry
        #endwhile
    else:
        while True:
            entry = date_start + (cycle * frequency)

            if entry > date_end:
                break

            cycle += 1
            yield entry
        #endwhile
    #endif

    return None
#enddef


DateOrDatetime = TypeVar("DateOrDatetime", datetime.date, datetime.datetime)
def clamp_date_list(
    date_list: List[DateOrDatetime],
    start_date: DateOrDatetime,
    end_date: DateOrDatetime
) -> List[datetime.datetime]:
    """Given a list of dates select only the ones that are greater than `start_date` and less than `end_date`."""

    if len(date_list) == 0: return []

    if not isinstance(date_list, list):
        raise ValueError(f"invalid date list '{date_list}'; must be a list")
    #endif

    if (
        not all(isinstance(item, date_list[0].__class__) for item in date_list) # check that all are the same type of the first
        or not isinstance(date_list[0], (datetime.date, datetime.datetime)) # then if the first is not accepted then no one will be
    ):
        raise ValueError(f"date_list must be a contiguous list of either datetime.date or datetime.datetime")
    #endif

    if (
        (start_date.__class__ != end_date.__class__)
        and (start_date.__class__ != date_list[0].__class__)
    ):
        raise ValueError(f"start_date and end_date must be the same type of the items in `date_list` (datetime.date or datetime.datetime)")
    #endif

    # at this point date_list is a list of all items of a single type (either datetime.date or datetime.datetime) and is the same type of
    # date_start and date_end

    output = []
    for entry in date_list:
        if entry >= start_date and entry <= end_date:
            output.append(entry)
    #endfor

    return output
#enddef

