def timeFormat(ms):
    time = ms/1000
    min, sec = divmod(time, 60)
    hour, min = divmod(min, 60)
    return ("%02d:%02d:%02d" % (hour, min, sec))