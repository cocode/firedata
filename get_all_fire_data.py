from requests import HTTPError

import get_az_fire_data
import get_ca_fire_data
import get_wa_fire_data
import get_us_fire_data


if __name__ == "__main__":
    functions = {
        "AZ": get_az_fire_data.run,
        "CA": get_ca_fire_data.run,
        "WA": get_wa_fire_data.run,
        "US": get_us_fire_data.run,
    }
    for st in functions:
        fn = functions.get(st)
        try:
            fn()
        except HTTPError as e:
            print(F"ERROR on getting {st} fire data", e)

    print("Done.")