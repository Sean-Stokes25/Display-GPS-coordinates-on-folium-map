import folium
import webbrowser
import time
import flask
import threading
from GPS_Parser import Parse_GPRMC
from GPRMC_emulator import GPRMC_emulator
import tracemalloc
tracemalloc.start()  #module to track memory
#---------
#**ISSUE**
#/gps is creating a new map every time i try to update marker this leads to memory errors
#---------

app = flask.Flask(__name__)

latlong = (55,55)
update_location_lock = threading.Lock()  #creates lock objcet that prevents a race condition between flask and update gps


@app.route("/gps")
def gps():
    print("gps endpoint hit")
    with update_location_lock:   #Using lock to prevent race condition
        lat, lon = latlong
    return {"lat": lat, "lon": lon}


@app.route("/")
def index():
    with update_location_lock:   #Using lock to prevent race condition
        current_latlong = latlong
    m = folium.Map(location=current_latlong, tiles="OpenStreetMap")
    
    map_var = m.get_name()  # gets the JS variable name folium assigned e.g. "map_a1b2c3"
    map_html = m.get_root().render()


#Problem
    polling_script = f"""
    <script>
    var marker = null;

    document.addEventListener("DOMContentLoaded", function() {{
        setTimeout(function() {{
            var map = {map_var};
            setInterval(function() {{
                fetch("/gps")
                    .then(r => r.json())
                    .then(data => {{
                        var latlng = [data.lat, data.lon];
                        if (marker) {{
                            marker.setLatLng(latlng);
                        }} else {{
                            marker = L.marker(latlng).addTo(map);
                        }}
                        map.panTo(latlng);
                    }});
            }}, 500);
        }}, 1000);
    }});
    </script>
    """

    return map_html + polling_script
    
def update_gps():
    global latlong
    while True:
        location = Parse_GPRMC(GPRMC_emulator())
        #Checks if valid nmea string(checksum)
        if location.valid:
            with update_location_lock:
                #turns the location from string to float
                latlong = tuple(float(x) for x in location.location())
        print("Gps updated")
        
        #Tracks memory usage
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')

        for stat in top_stats[:10]:
            print(stat)

if __name__ == "__main__":
    #runs update_gps on a differnt thread so index can run at the same time
    threading.Thread(target=update_gps, daemon=True).start()
    webbrowser.open("http://127.0.0.1:5050")
    from waitress import serve
    serve(app, host="127.0.0.1", port=5050)
    



