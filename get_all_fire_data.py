from requests import HTTPError

import get_ca_fire_data
import get_wa_fire_data
import get_us_fire_data



if __name__ == "__main__":
    try:
        get_wa_fire_data.run()
    except HTTPError as e:
        print("ERROR on getting WA fire data", e)
    # Keep trying, the other site may not be having problems.
    try:
        get_ca_fire_data.run()
    except HTTPError as e:
        print("ERROR on getting CA fire data", e)
    try:
        get_us_fire_data.run()
    except HTTPError as e:
        print("ERROR on getting US fire data", e)
    print("Done.")