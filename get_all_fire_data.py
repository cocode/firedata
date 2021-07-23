from typing import Callable

import get_az_fire_data
import get_ca_alt_fire_data
import get_ca_fire_data
import get_wa_fire_data
import get_us_fire_data


def run():
    functions: dict[str, Callable[[], None]] = {
        # "AZ": get_az_fire_data.run,
        "CA": get_ca_fire_data.run,
        "CA_ALT": get_ca_alt_fire_data.run,
        "WA": get_wa_fire_data.run,
        "US": get_us_fire_data.run,
    }
    return_code = 0
    for st, fn in functions.items():
        try:
            fn()
        except Exception as e:
            print(F"ERROR on getting {st} fire data", e)
            return_code = 1

    get_az_fire_data.run(get_az_fire_data.DATA_STORE_PATH)
    print("Done.")
    return return_code


if __name__ == "__main__":
    run()  # pragma: no cover