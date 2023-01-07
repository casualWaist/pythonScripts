# this is literally the same code as G-trick Drag with one varibale changed
# it exsists because we had two knife tools and two scripts was faster than any prompt to input which tool
# just right click on the tool script, hit run, and there you go

from __future__ import division
from decimal import Decimal
import operator
import math


def fiducialvalues(rawline, nextline):
    i = rawline.find(',')
    xo = Decimal(rawline[2:i])
    i += 1
    ii = rawline.find(';')
    yo = Decimal(rawline[i:ii])
    i = 0
    ti = 0
    c = 0
    while c < 10:
        i = nextline[ti:].find(',')
        i += 1
        ti = ti + i
        c += 1
    ii = nextline[ti:].find(',') + ti
    xt = Decimal(nextline[ti:ii])
    ii += 1
    iii = nextline[ii:].find(',') + ii
    yt = Decimal(nextline[ii:iii])
    #print('fidvalues', xo, xt, yo, yt)
    return xo, xt, yo, yt


def getfiducial(rawline, nextline):
    xo, xt, yo, yt = fiducialvalues(rawline, nextline)
    x = (xo + xt) / 2
    y = (yo + yt) / 2
    point = [x,y]
    #print('getfid', point)
    return point


def getrect(rawline, xoff, yoff):
    i = rawline.find(',')
    xone = Decimal(rawline[2:i]) + xoff
    i += 1
    rawline = rawline[i:]
    i = rawline.find(',')
    yone = Decimal(rawline[:i]) + yoff
    i += 1
    rawline = rawline[i:]
    i = rawline.find(',')
    xtwo = Decimal(rawline[:i]) + xoff
    i += 1
    rawline = rawline[i:]
    i = rawline.find(',')
    ytwo = Decimal(rawline[:i]) + yoff
    i += 1
    rawline = rawline[i:]
    i = rawline.find(',')
    xthree = Decimal(rawline[:i]) + xoff
    i += 1
    rawline = rawline[i:]
    i = rawline.find(',')
    ythree = Decimal(rawline[:i]) + yoff
    i += 1
    rawline = rawline[i:]
    i = rawline.find(',')
    xfour = Decimal(rawline[:i]) + xoff
    i += 1
    rawline = rawline[i:]
    i = rawline.find(';')
    yfour = Decimal(rawline[:i]) + yoff
    gcode = 'G00 X%s Y%s Z-0.25\nM12\nG01 X%s Y%s Z0.01 F0.83\nG01 X%s Y%s Z0.01 F1.67\nG01 X%s Y%s Z0.01\nG01 X%s Y%s Z0.01\nG01 X%s Y%s Z0.01\nG00 Z-0.25\nM22\n' % (
    xfour, yfour, xfour, yfour, xone, yone, xtwo, ytwo, xthree, ythree, xfour, yfour)
    return [xfour, yfour, gcode]


def commacount(line):
    x = line.count(',')
    #print(x)
    return x


def nobz(line):
    if 'BZ' in line:
        #print('nobz False')
        return False
    else:
        #print('nobz True')
        return True


def isfiducial(firstline, line):
    xo, xt, yo, yt = fiducialvalues(firstline, line)
    x = xo - xt
    y = yo - yt
    if x < 0:
        x = x * -1
    if y < 0:
        y = y * -1
    if x == 0.25 and y == 0.0 or x == 0.0 and y == 0.25:
        #print('isfid True')
        return True
    else:
        #print('isfid False')
        return False


def fiducialoffset(fids):
    fids.sort(key = operator.itemgetter(0,1))
    xoff = Decimal(0.125) - fids[0][0]
    yoff = Decimal(0.125) - fids[0][1]
    final = ''
    for point in fids:
        x = point[0] + xoff
        y = point[1] + yoff
        final = final + 'G00 X%s Y%s Z-0.25\nM12\nG01 X%s Y%s Z0.0 F0.83\nG01 X%s Y%s Z0.01 F1.67\nG01 X%s Y%s Z0.0\nG00 Z-0.25\nM22\n' % (x,y,x,y,x,y,x,y)
    #print('fidoff', final, xoff, yoff)
    return final, xoff, yoff


def splitvalues(line):
    values = line.split(',')
    values = [values[i:i+2] for i in range(0, len(values), 2)]
    #print('splitvalues', values)
    return values


def checktol(lastx, lasty, x, y):
    if abs(lastx - x) < 0.01 and abs(lasty - y) < 0.01:
        #print('checktol False')
        return False
    else:
        #print('checktol True')
        return True


def linetoshape(lines, xoff, yoff):
    shape = []
    return shape

def get_p_on_bez(curve, t):
    x = curve[0][0]*(Decimal(1.0)-t)**Decimal(3.0)+curve[1][0]*Decimal(3.0)*(Decimal(1.0)-t)**Decimal(2.0)*t+curve[2][0]*Decimal(3.0)*(Decimal(1.0)-t)*t**Decimal(2.0)+curve[3][0]*t**Decimal(3.0)
    y = curve[0][1]*(Decimal(1.0)-t)**Decimal(3.0)+curve[1][1]*Decimal(3.0)*(Decimal(1.0)-t)**Decimal(2.0)*t+curve[2][1]*Decimal(3.0)*(Decimal(1.0)-t)*t**Decimal(2.0)+curve[3][1]*t**Decimal(3.0)
    #print('point of bez', x, y)
    return [x,y]

def midpoint(p0, p1):
    x = (p0[0] + p1[0])/Decimal(2.0)
    y = (p0[1] + p1[1])/Decimal(2.0)
    #print('midpoint', x, y)
    return [x,y]

def slope(p0, p1):
    m = (p1[1] - p0[1])/(p1[0] - p0[0])
    #print('slope', m)
    return m

def perp_slope(m):
    pm = Decimal(-1.0)/m
    #print('perp slope', pm)
    return pm

def yinter(p0, m):
    b = p0[1] - (m * p0[0])
    #print('y intersept', b)
    return b

def intersect(b0, b1, m0, m1):
    x = (b1 - b0)/(m0 - m1)
    y = m0 * x + b0
    y2 = m1 * x + b1
    #print('intersect', x, y, y2)
    return [x,y]

def distance(p0, p1):
    d = math.sqrt((p1[0] - p0[0])**Decimal(2.0) + (p1[1] - p0[1])**Decimal(2.0))
    #print('distance', d)
    return d

def center_radius(points):
    start = points[0]
    mid = points[1]
    end = points[2]
    sm = midpoint(start, mid)
    me = midpoint(mid, end)
    ssm = perp_slope(slope(start, mid))
    sme = perp_slope(slope(mid, end))
    c = intersect(yinter(sm, ssm), yinter(me, sme), ssm, sme)
    r = distance(c, start)
    return c, r

def bez_is_line(bez):
    a = ((bez[0][0] - bez[1][0]) * (bez[3][1] - bez[1][1]) - (bez[0][1] - bez[1][1]) * (bez[3][0] - bez[1][0]))
    b = ((bez[0][0] - bez[2][0]) * (bez[3][1] - bez[2][1]) - (bez[0][1] - bez[2][1]) * (bez[3][0] - bez[2][0]))
    #only checks if point 1 & 2 are on line not in between start and end points
    if Decimal(-0.00009) < a < Decimal(0.00009) and Decimal(-0.00009) < b < Decimal(0.00009):
        return True
    else:
        return False

def get_arcs(bez):
    if bez_is_line(bez):
        return [[bez[3]]]
    else:
        ends_centers = []
        et = Decimal(1.0)
        st = Decimal(0.0)
        step = Decimal(0.5)
        v = True
        last = False
        start = get_p_on_bez(bez, st)
        mid = get_p_on_bez(bez, et / Decimal(2.0))
        end = get_p_on_bez(bez, et)
        new_mid = mid
        new_end = end
        center, radius = center_radius([start, mid, end])

        while v:
            new_center, new_radius = center_radius([start, new_mid, new_end])
            n = et - st
            test1 = get_p_on_bez(bez, st + (n * Decimal(0.25)))
            test2 = get_p_on_bez(bez, et - (n * Decimal(0.25)))
            t1 = abs(radius - distance(test1, new_center))
            t2 = abs(radius - distance(test2, new_center))
            if t1 < Decimal(0.001) and t2 < Decimal(0.001):
                if et == Decimal(1.0):
                    ends_centers.append([end, center])
                    v = False
                else:
                    et = et + ((et - st) * step)
                    step = step * Decimal(0.5)
                    if et > Decimal(1.0):
                        et = Decimal(1.0)
                    new_end = get_p_on_bez(bez, et)
                    new_mid = get_p_on_bez(bez, st + (et - st)*Decimal(0.5))
                    last = True
            else:
                if last:
                    ends_centers.append([end, center])
                    step = Decimal(0.5)
                    st = et
                    et = Decimal(1.0)
                    start = get_p_on_bez(bez, st)
                    mid = get_p_on_bez(bez, st + (et - st)*Decimal(0.5))
                    end = get_p_on_bez(bez, et)
                    new_mid = mid
                    new_end = end
                    center, radius = center_radius([start, mid, end])
                    last = False
                else:
                    et = et - ((et - st)* step)
                    step = step * Decimal(0.5)
                    new_end = get_p_on_bez(bez, et)
                    new_mid = get_p_on_bez(bez, st + (et - st)*Decimal(0.5))
                    end = new_end
                    mid = new_mid
                    center, radius = center_radius([start, mid, end])
        return ends_centers

def mkreadyforbez(points):
    final = []
    while len(points) > 1:
        final.append([points[0], points[1], points[2], points[3]])
        del points[:3]
    return final

def isclockwise(start, end, center):
    c = ((start[0] - center[0]) * (end[1] - center[1])) - ((start[1] - center[1]) * (end[0] - center[0]))
    if c < Decimal(0.0):
        return True
    else:
        return False

def getbz(lines, xoff, yoff):
    shape = ''
    addf = True
    lastx = 0
    lasty = 0
    for line in lines:
        line = line.replace(';\n', '')
        if 'PA' in line:
            line = line.replace('PA', '')
            values = splitvalues(line)
            for point in values:
                x = Decimal(point[0]) + xoff
                y = Decimal(point[1]) + yoff
                if len(shape) == 0:
                    shape = 'G00 X%s Y%s Z-0.25\nM12\nG01 X%s Y%s Z0.01 F0.83\n' % (x, y, x, y)
                    lastx = x
                    lasty = y
                elif checktol(lastx, lasty, x, y):
                    if addf:
                        shape = shape + 'G01 X%s Y%s Z0.01 F1.67\n' % (x,y)
                        addf = False
                    else:
                        shape = shape + 'G01 X%s Y%s Z0.01\n' % (x,y)
                    lastx = x
                    lasty = y
        elif 'PD' in line:
            line = line.replace('PD', '')
            values = splitvalues(line)
            for point in values:
                x = Decimal(point[0]) + xoff
                y = Decimal(point[1]) + yoff
                if checktol(lastx, lasty, x, y):
                    if addf:
                        shape = shape + 'G01 X%s Y%s Z0.01 F1.67\n' % (x,y)
                        addf = False
                    else:
                        shape = shape + 'G01 X%s Y%s Z0.01\n' % (x,y)
                    lastx = x
                    lasty = y
        elif 'BZ' in line:
            line = line.replace('BZ', '')
            values = splitvalues(line)
            for point in values:
                point[0] = Decimal(point[0]) + xoff
                point[1] = Decimal(point[1]) + yoff
            values = [[lastx, lasty]] + values
            bezs = mkreadyforbez(values)
            arcs = []
            for bez in bezs:
                arcs.extend(get_arcs(bez))
            for arc in arcs:
                if len(arc) == 1:
                    x = arc[0][0]
                    y = arc[0][1]
                    if addf:
                        shape = shape + 'G01 X%0.4f Y%0.4f Z0.01 F1.67\n' % (x, y)
                        addf = False
                    else:
                        shape = shape + 'G01 X%0.4f Y%0.4f Z0.01\n' % (x, y)
                    lastx = x
                    lasty = y
                else:
                    x = arc[0][0]
                    y = arc[0][1]
                    i = arc[1][0]
                    j = arc[1][1]
                    g = 'G03'
                    if isclockwise([lastx, lasty], [x, y], [i,j]):
                        g = 'G02'
                    if addf:
                        shape = shape + '%s X%0.4f Y%0.4f I%0.4f J%0.4f F1.67\n' % (g, x, y, i, j)
                        addf = False
                    else:
                        shape = shape + '%s X%0.4f Y%0.4f I%0.4f J%0.4f\n' % (g, x, y, i, j)
                    lastx = x
                    lasty = y
    return [lastx, lasty, shape + 'G00 Z-0.25\nM22\n']

with open('//aaserverbackup/home/1 Knife Rout/1.rtl') as origin:
    lines = origin.readlines()
    l = 0
    f = 0
    preamble = 'M90\nG90\nG70\nG75\nG97 S24000\nG00 T99\n'
    fiducials = []
    finalist = []
    shapes = []
    toolchange = 'G97 S24000\nG00 T31\n'
    ps = 'G98 P147 D1\nM02'
    r = []
    while f < 4:
        line = lines[l]
        if 'PD;' in line and commacount(lines[l + 1]) == 23 and isfiducial(lines[l - 1], lines[l + 1]):
            fiducials.append(getfiducial(lines[l - 1], lines[l + 1]))
            f += 1
            r = r + [l]
        l += 1
    finalfiducials, xoff, yoff = fiducialoffset(fiducials)
    while f > 0:
        del lines[r[-1]]
        del r[-1]
        f -= 1
    l = 0
    while l < len(lines):
        line = lines[l]
        if 'PD' in line and line[2] != ';':
            if commacount(line) == 7 and nobz(lines[l + 1]):
                shapes.append(getrect(line, xoff, yoff))
            else:
                shape = [lines[l - 1]]
                pu = True
                t = 0
                while pu:
                    if 'PU;' in lines[l + t]:
                        pu = False
                    else:
                        shape.append(lines[l + t])
                    t += 1
                shapes.append(getbz(shape, xoff, yoff))
        elif 'PD;' in line:
            shape = [lines[l - 1]]
            pu = True
            t = 1
            while pu:
                if 'PU;' in lines[l + t]:
                    pu = False
                else:
                    shape.append(lines[l + t])
                t += 1
            shapes.append(getbz(shape, xoff, yoff))
        l += 1
    shapes.sort(key=operator.itemgetter(0,1))
    for shape in shapes:
        finalist.append(shape[2])
    final = preamble + finalfiducials + toolchange + ''.join(finalist) + ps
    file = open('C:/DncFiles/007Today/toDo.cnc', 'w')
    file.write(final)
    file.close()
