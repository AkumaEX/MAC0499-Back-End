import folium


class HotspotViewer(object):

    def __init__(self, clusters_data):
        self._clusters_data = clusters_data
        self.folium_map = folium.Map(location=(-23.5489, -46.6388), zoom_start=14)
        circles, polygons = self._get_data()
        self.folium_map.add_child(polygons)
        self.folium_map.add_child(circles)

    def get_result(self):
        return self.folium_map

    def save_map_to(self, address):
        with open(address, 'w') as f:
            f.write(self.folium_map._repr_html_())

    def _get_data(self):
        circles = folium.FeatureGroup(name='Circles')
        polygons = folium.FeatureGroup(name='Polygons')
        for data in self._clusters_data:
            features = data['features']
            for feature in features:
                if feature['geometry']['type'] == 'Point':
                    date = feature['properties']['date']
                    time = feature['properties']['time']
                    location = feature['geometry']['coordinates']
                    circles.add_child(self._new_circle(date, time, location))
                elif feature['geometry']['type'] == 'LineString':
                    hotspot = feature['hotspot']
                    locations = feature['geometry']['coordinates']
                    if locations:
                        polygons.add_child(self._new_polygon(locations, hotspot))
        return circles, polygons

    @staticmethod
    def _new_circle(date, time, location):
        return folium.Circle(
            location=location,
            popup='Data: {0}\nHora: {1}'.format(date, time),
            color='red',
            radius=10,
            fill=True
        )

    @staticmethod
    def _new_polygon(locations, hotspot):
        return folium.Polygon(
            locations=locations,
            fill_color='red' if hotspot else 'green',
            fill_opacity=0.2,
            color='black',
            weight=1
        )
