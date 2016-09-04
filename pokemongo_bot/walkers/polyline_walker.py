from geographiclib.geodesic import Geodesic

from pokemongo_bot.walkers.step_walker import StepWalker
from polyline_generator import PolylineObjectHandler


class PolylineWalker(StepWalker):
    def get_next_position(self, origin_lat, origin_lng, origin_alt, dest_lat, dest_lng, dest_alt, distance):
        polyline = PolylineObjectHandler.cached_polyline((self.bot.position[0], self.bot.position[1]), (dest_lat, dest_lng), distance, google_map_api_key=self.bot.config.gmapkey)

        while True:
            _, (dest_lat, dest_lng) = polyline._step_dict[polyline._step_keys[polyline._last_step]]
            polyline._last_pos = (dest_lat, dest_lng)
            dest_alt = polyline.get_alt() or origin_alt

            next_lat, next_lng, next_alt = super(PolylineWalker, self).get_next_position(origin_lat, origin_lng, origin_alt, dest_lat, dest_lng, dest_alt, distance)

            if polyline._last_step == len(polyline._step_keys) - 1:
                break
            else:
                travelled = Geodesic.WGS84.Inverse(origin_lat, origin_lng, next_lat, next_lng)["s12"]
                remaining = Geodesic.WGS84.Inverse(next_lat, next_lng, dest_lat, dest_lng)["s12"]
                step_distance = Geodesic.WGS84.Inverse(origin_lat, origin_lng, dest_lat, dest_lng)["s12"]

                if remaining < (self.precision + self.epsilon):
                    polyline._last_step += 1
                    distance = abs(distance - step_distance)
                else:
                    distance = abs(distance - travelled)

                if distance > (self.precision + self.epsilon):
                    origin_lat, origin_lng, origin_alt = dest_lat, dest_lng, dest_alt
                else:
                    break

        polyline._last_pos = (next_lat, next_lng)

        return next_lat, next_lng, next_alt
