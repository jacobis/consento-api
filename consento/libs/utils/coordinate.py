
def coordinate_swapper(latlng):
    latlng = [float(i) for i in latlng]
    if len(latlng) == 4:
        latmin, lngmin, latmax, lngmax = \
        latlng[0], latlng[1], latlng[2], latlng[3]

        if latmin > latmax:
            latmin, latmax = latmax, latmin

        if lngmin > lngmax:
            lngmin, lngmax = lngmax, lngmin

        latlng = [latmin, lngmin, latmax, lngmax]

    return latlng