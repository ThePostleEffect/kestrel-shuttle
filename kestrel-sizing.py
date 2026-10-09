"""KESTREL concept screening model. Standard library only; not a flight model.

Run: python kestrel-sizing.py
All vehicle values are proposed design assumptions, not qualified specifications.
Earth is spherical, nonrotating; no drag, finite-burn, pointing or coupled thermal model.
"""
import json
import math


def calculate():
    mu = 3.986004418e14  # m^3/s^2, standard Earth gravitational parameter
    radius = 6_371_000.0  # m, mean spherical Earth radius used consistently
    altitude = 400_000.0
    r = radius + altitude
    period = 2 * math.pi * math.sqrt(r**3 / mu)
    eclipse = period * math.asin(radius / r) / math.pi  # beta=0, point Sun
    sunlight = period - eclipse
    energy = mu / radius - mu / (2 * r)  # J/kg, surface at rest to circular orbit
    g0, isp = 9.80665, 315.0
    dry, crew, cargo, propellant, held_prop = 18_000, 1_000, 3_000, 3_000, 400
    initial = dry + crew + cargo + propellant
    final = initial - (propellant - held_prop)
    dv = g0 * isp * math.log(initial / final)
    perigee = radius + 50_000
    transfer_a = (r + perigee) / 2
    deorbit = math.sqrt(mu/r) - math.sqrt(mu * (2/r - 1/transfer_a))
    plane_change = 2 * math.sqrt(mu/r) * math.sin(math.radians(1)/2)
    load, array = 8.0, 25.0  # kW delivered load and reference sunlit bus output
    eclipse_kwh = load * eclipse/3600
    min_array = load + eclipse_kwh/(0.90 * sunlight/3600)
    solar_area = array*1000/(1361*0.29*0.78)
    usable_battery = 40*0.80*0.80*0.92
    sigma, emissivity, environment = 5.670374419e-8, 0.85, 150
    warm_flux = emissivity*sigma*310**4 - environment
    cool_flux = emissivity*sigma*285**4 - environment
    warm_area, cool_area = 8_000/warm_flux, 4_000/cool_flux
    mass_allocations_t = {
        'Structure, pressure shell and aero surfaces': 5.2,
        'Thermal protection': 2.2,
        'Landing gear and flight controls': 1.1,
        'Orbital propulsion hardware and tanks': 1.2,
        'Life support hardware': 1.1,
        'Solar, batteries and electrical distribution': 1.5,
        'Thermal control hardware and working fluids': 0.7,
        'Avionics and communications': 0.5,
        'Docking, cassette interface and inspection arm': 1.0,
        'Cabin interior and seats': 0.5,
    }
    assert math.isclose(sum(mass_allocations_t.values()),15.0)
    assert initial == 25_000 and final == 22_400
    return {
        'status': 'Concept assumptions and first-order calculations; not flight validated',
        'constants': {'mu_m3_s2':mu, 'earth_radius_m':radius, 'orbit_altitude_m':altitude, 'g0_m_s2':g0},
        'mass_allocations_t': mass_allocations_t,
        'dry_basic_t':15, 'dry_margin_t':3, 'dry_total_t':18,
        'orbital_insertion_t':initial/1000,
        'launch_adapter_escape_shroud_mass': 'Additional; unresolved; not included in 25 t',
        'orbit_speed_km_s':math.sqrt(mu/r)/1000,
        'orbit_period_min':period/60,
        'maximum_eclipse_min':eclipse/60,
        'sunlight_min':sunlight/60,
        'ideal_orbital_energy_MJ_kg':energy/1e6,
        'ideal_orbital_energy_kWh_kg':energy/3.6e6,
        'ideal_orbital_energy_25t_MWh':energy*initial/3.6e9,
        'orbiter_main_maneuver_delta_v_m_s':dv,
        'allocated_main_delta_v_m_s':330,
        'unallocated_main_delta_v_m_s':dv-330,
        'ideal_deorbit_to_50km_perigee_m_s':deorbit,
        'one_degree_plane_change_m_s':plane_change,
        'eclipse_load_kWh':eclipse_kwh,
        'minimum_sunlit_generation_kW':min_array,
        'solar_active_area_m2':solar_area,
        'battery_nameplate_kWh':40,
        'battery_delivered_EOL_kWh':usable_battery,
        'single_pack_emergency_hours_at_4kW':usable_battery/2/4,
        'warm_radiator_area_m2':warm_area,
        'cool_radiator_area_m2':cool_area,
        'radiator_total_effective_area_m2':warm_area+cool_area,
        'stowed_thermal_energy_8kW_90min_MJ':8*1.5*3.6,
        'sstO_remaining_fraction_at_380s_9300m_s':math.exp(-9300/(g0*380)),
        'sstO_remaining_fraction_at_450s_9300m_s':math.exp(-9300/(g0*450)),
        'scope_limits': ['No launch trajectory or engine sizing', 'No aerodynamic/structural closure',
                         'No validated escape envelope', 'No validated radiator view factors',
                         'No cost, lifecycle energy or reliability prediction']
    }


if __name__ == '__main__':
    print(json.dumps(calculate(), indent=2))
