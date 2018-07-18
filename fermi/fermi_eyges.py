import numpy as np
from scipy.integrate import quad
from ..physics import energy_to_pv
from .stopping import residual_energy


def fermi_eyges_integrals(u, initial_energy, thickness, material, db, t, n):
    return (thickness-u)**n * t.t(
        energy_to_pv(residual_energy(material, u, initial_energy, db=db)),
        energy_to_pv(initial_energy),
        db=db,
        material=material
    )


def compute_energy_dispersion(energy, material):
    # Required transmitted energy as E
    # 4th degree polynomial fits of Robin data with no cuts
    E = energy
    if material == 'beryllium':
        return 6.388e-11*E**4 - 4.906e-08*E**3 + 1.46e-05*E**2 - 0.002062*E + 0.1214
    elif material == 'graphite':
        return 1.082e-10*E**4 - 7.794e-08*E**3 + 2.113e-05*E**2 - 0.002629*E + 0.1332
    elif material == 'alluminum':
        return 9.625e-11*E**4 - 6.95e-08*E**3 + 1.897e-05*E**2 - 0.002389*E + 0.1234
    elif material == 'diamond':
        return 4.997e-10*E**4 - 3.04e-07*E**3 + 6.783e-05*E**2 - 0.006684*E**2 + 0.2572
    else:
        return 0.00/E


def compute_losses(energy, material):
    # Required transmitted energy as E
    # 4th degree polynomial fits of Robin data with no cuts
    E = energy
    if material == 'beryllium':
        return -1.28592847e-10*E**4 + 8.86840237e-08*E**3 - 1.46323515e-05*E**2 + 2.21159797e-03*E + 5.50841457e-01
    elif material == 'graphite':
        return -2.31889627e-11*E**4 + 2.56333388e-08*E**3 - 2.59110160e-06*E**2 + 1.12196496e-03*E + 6.37417688e-01
    elif material == 'alluminum':
        return -7.978e-11*E**4 + 5.157e-08*E**3 - 6.313e-06*E**2 + 0.001242*E + 0.6474
    elif material == 'diamond':
        return -1.3e-10*E**4 + 8.528e-08*E**3 - 1.434e-05*E**2 + 0.002085*E + 0.6084
    else:
        return 1.0


def compute_fermi_eyges(material, energy, thickness, db, t, with_dpp=True, with_losses=True, **kwargs):
    a = [
        quad(fermi_eyges_integrals, 0, thickness, args=(energy, thickness, material, db, t, 0))[0],  # Order 0
        1e-2*quad(fermi_eyges_integrals, 0, thickness, args=(energy, thickness, material, db, t, 1))[0],  # Order 1
        1e-4*quad(fermi_eyges_integrals, 0, thickness, args=(energy, thickness, material, db, t, 2))[0],  # Order 2
    ]
    b = np.sqrt(a[0] * a[2] - a[1]**2)  # Emittance in m.rad
    if with_dpp:
        dpp = (compute_energy_dispersion(residual_energy(material, thickness, energy, db=db), material))**2
    else:
        dpp = 0
    if with_losses:
        loss = compute_losses(residual_energy(material, thickness, energy, db=db), material)
    else:
        loss = 0

    return {
        'A': a,
        'B': b,
        'E_R': residual_energy(material, thickness, energy, db=db),
        'DPP': dpp,
        'LOSS': loss,
        'TWISS_ALPHA': -a[1] / b,
        'TWISS_BETA': a[2] / b,
        'TWISS_GAMMA': a[0] / b,
    }
