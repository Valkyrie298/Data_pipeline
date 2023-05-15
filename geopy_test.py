import geocoder
result = geocoder.arcgis(location="FXJG+PF7, 028 Yết Kiêu, Kim Tân, TX.Lào Cai, Lào Cai, Vietnam")
if result.ok:
    lat, lon= result.latlng
else:
    raise Exception("Got bad result :-(")

print(lat)
print(lon)