import get_cal_fire_data
import get_wa_fire_data
import get_us_fire_data



if __name__ == "__main__":
    get_wa_fire_data.run()
    get_cal_fire_data.run()
    get_us_fire_data.run()
    print("Done.")