# Display-GPS-coordinates-on-folium-map

I am using an NMEA GPRMC emmulator i wrote to generate random coordinates i am then then displaying these coordinates on a folium map

I am updating the markers coordinates and generating the map on 2 different threads in order to avoid a race case i have to use a mutex (thraeding.lock)

I am facing out of memory errors because the folium map is regenerated after every coordinate update

This map is then served to a local webpage using flask
