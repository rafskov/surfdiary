from buoyant import Buoy


session_beach = 'Pacheco'

#get buoy data for all beaches
sf = Buoy(46237)
santacruz = Buoy(46042)
santacruzbeaches =['PleasurePoint','4mile']

#map buoy to beach
if session_beach not in santacruzbeaches:
    waves = sf.waves
else:
    waves = santacruz.waves

swell_period = waves['sea_surface_swell_wave_period']
swell_height = waves['sea_surface_swell_wave_significant_height']
swell_direction = 360-waves['sea_surface_swell_wave_to_direction']+'degrees'

print(swell_height,swell_period,swell_direction)
