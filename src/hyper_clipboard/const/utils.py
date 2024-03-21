from datetime import datetime,timezone

def make_id_from_name(name:str)->int:
    list_ = [str(ord(c)) for c in name]
    return int("" . join(list_[:4]))

def get_milli_unix_time()->int:
    utc_time = datetime.now(timezone.utc)
    float_unix_time = utc_time.timestamp()
    mili_unix_time = int(float_unix_time*1000)
    return mili_unix_time