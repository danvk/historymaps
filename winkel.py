'''A class to help deal with the Winkel Tripel projection.'''
# -*- coding: utf-8 -*-

import math

halfpi = math.pi / 2
epsilon = 1e-6

def sinci(x):
    return x / math.sin(x) if x else 1


def acos(x):
    if x > 1:
        return 0
    elif x < -1:
        return math.pi
    else:
        return math.acos(x)


def aitoff(Lambda, phi):
    '''
    Lambda \in [-pi, pi]
    phi \in [-pi/2, pi/2]
    '''
    cosphi = math.cos(phi)
    Lambda = Lambda / 2.0
    sinci_alpha = sinci(acos(cosphi * math.cos(Lambda)))
    return (
        2 * cosphi * math.sin(Lambda) * sinci_alpha,
        math.sin(phi) * sinci_alpha
    )


class ScaledWinkel(object):
    def __init__(self, maxx, maxy, center_lon):
        self._maxx = maxx
        self._maxy = maxy
        self._center_lon = center_lon
        self._w = Winkel()
        self._maxunitx, _ = self._w.project(math.pi, 0.0)
        _, self._maxunity = self._w.project(0.0, math.pi/2.0)

    def recenter_lon(self, lon):
        lon = lon + self._center_lon
        if lon < -180.0:
            lon += 360.0
        elif lon > 180.0:
            lon -= 360.0
        return lon

    def r2d(self, r):
        return 180.0 / math.pi * r

    def invert(self, x, y):
        '''Returns lon, lat. East and North are positive.'''
        unitx = (2 * (float(x) / self._maxx) - 1) * self._maxunitx
        unity = (2 * (float(y) / self._maxy) - 1) * self._maxunity
        Lambda, phi = self._w.invert(unitx, unity)
        lon, lat = self.r2d(Lambda), -self.r2d(phi)
        lon = self.recenter_lon(lon)
        return lon, lat

    def project(self, Lambda, phi):
        pass


class Winkel(object):
    def __init__(self):
        pass

    def project(self, Lambda, phi):
        coords = aitoff(Lambda, phi)
        return (
          (coords[0] + Lambda / halfpi) / 2,
          (coords[1] + phi) / 2
        )

    def invert(self, x, y):
        Lambda = float(x)
        phi = float(y)
        i = 25
        while True:
            cos_phi = math.cos(phi)
            sin_phi = math.sin(phi)
            sin_2phi = math.sin(2.0 * phi)
            sin2phi = sin_phi * sin_phi
            cos2phi = cos_phi * cos_phi
            sinlambda = math.sin(Lambda)
            coslambda_2 = math.cos(Lambda / 2.0)
            sinlambda_2 = math.sin(Lambda / 2.0)
            sin2lambda_2 = sinlambda_2 * sinlambda_2
            C = 1.0 - cos2phi * coslambda_2 * coslambda_2
            if C != 0:
                F = 1.0 / C
                E = acos(cos_phi * coslambda_2) * math.sqrt(F)
            else:
                E = 0.0
                F = 0.0
            fx = 0.5 * (2.0 * E * cos_phi * sinlambda_2 + Lambda / halfpi) - x
            fy = 0.5 * (E * sin_phi + phi) - y
            deltaxdeltaLambda = 0.5 * F * (cos2phi * sin2lambda_2 + E * cos_phi * coslambda_2 * sin2phi) + 0.5 / halfpi
            deltaxdeltaphi = F * (sinlambda * sin_2phi / 4.0 - E * sin_phi * sinlambda_2)
            deltaydeltaLambda = 0.125 * F * (sin_2phi * sinlambda_2 - E * sin_phi * cos2phi * sinlambda)
            deltaydeltaphi = 0.5 * F * (sin2phi * coslambda_2 + E * sin2lambda_2 * cos_phi) + .5
            denominator = deltaxdeltaphi * deltaydeltaLambda - deltaydeltaphi * deltaxdeltaLambda
            deltaLambda = (fy * deltaxdeltaphi - fx * deltaydeltaphi) / denominator
            deltaphi = (fx * deltaydeltaLambda - fy * deltaxdeltaLambda) / denominator
            Lambda -= deltaLambda
            phi -= deltaphi

            i -= 1
            if (abs(deltaLambda) > epsilon or abs(deltaphi) > epsilon) and i > 0:
                continue
            else:
                break
        return [Lambda, phi]

