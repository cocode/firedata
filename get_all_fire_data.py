from requests import HTTPError
from typing import Callable

import get_az_fire_data
import get_ca_fire_data
import get_wa_fire_data
import get_us_fire_data


def run():
    functions: dict[str, Callable[[], None]] = {
        "AZ": get_az_fire_data.run,
        "CA": get_ca_fire_data.run,
        "WA": get_wa_fire_data.run,
        "US": get_us_fire_data.run,
    }
    for st, fn in functions.items():
        try:
            fn()
        except HTTPError as e:
            print(F"ERROR on getting {st} fire data", e)

    print("Done.")


if __name__ == "__main__":
    run()  # pragma: no cover