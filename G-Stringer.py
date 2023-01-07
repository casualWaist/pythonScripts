# script that is designed to edit a G code file by finding overlapping or adjacent line segments and either removing or combining them
# the file is initialized by external CAM software as an array of rectangles of the same size with no space between them (sheet of printed decals for cutting)
# the goal is to combine the rectangles into grid lines decreasing the machining time of large files


import decimal


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

with open('C:/DncFiles/007Today/toDo.cnc') as f:
    start_g_code = f.readlines()
    print(len(start_g_code))


def get_x_y_value(g_line):
    a = g_line.index('X')
    a += 1
    b = g_line.index('Y')
    b -= 1
    x = decimal.Decimal(g_line[a:b])
    c = g_line.index('Z')
    b += 2
    c -= 1
    y = decimal.Decimal(g_line[b:c])
    now = Point(round(x, 3), round(y, 3))
    return now


def get_f_value(g_line):
    a = g_line.index('F')
    a += 1
    b = g_line.index('\n')
    f = g_line[a:b]
    return decimal.Decimal(f)


def save_and_open(final_g):
    print(len(final_g.splitlines(True)))
    file = open('C:/DncFiles/007Today/toDo.cnc', 'w')
    file.write(final_g)
    file.close()


def point_equal(a, b):
    if getattr(a, 'x') == getattr(b, 'x') and getattr(a, 'y') == getattr(b, 'y'):
        return True
    else:
        return False


def compare_lines(a, b, c, d):
    if getattr(a, 'x') == getattr(d, 'x') and getattr(a, 'y') == getattr(d, 'y') and getattr(b, 'x') == getattr(c, 'x') and getattr(b, 'y') == getattr(c, 'y'):
        return True
    else:
        return False


def should_connect(a, b, c, d):
    if getattr(a, 'x') == getattr(d, 'x') and getattr(a, 'y') == getattr(d, 'y'):
        if getattr(b, 'x') == getattr(c, 'x') or getattr(b, 'y') == getattr(c, 'y'):
            return True
        else:
            return False
    elif getattr(a, 'x') == getattr(c, 'x') and getattr(a, 'y') == getattr(c, 'y'):
        if getattr(b, 'x') == getattr(d, 'x') or getattr(b, 'y') == getattr(d, 'y'):
            return True
        else:
            return False
    elif getattr(b, 'x') == getattr(c, 'x') and getattr(b, 'y') == getattr(c, 'y'):
        if getattr(a, 'x') == getattr(d, 'x') or getattr(a, 'y') == getattr(d, 'y'):
            return True
        else:
            return False
    elif getattr(b, 'x') == getattr(d, 'x') and getattr(b, 'y') == getattr(d, 'y'):
        if getattr(a, 'x') == getattr(c, 'x') or getattr(a, 'y') == getattr(c, 'y'):
            return True
        else:
            return False
    else:
        return False


def check_for_overlap(pointa, pointb, i):
    sdindex = 0
    fdindex = 0
    answer = False
    while i < len(start_g_code) - 1:
        line = start_g_code[i]
        line_after = start_g_code[i + 1]
        if 'G01' in line and 'G01' in line_after:
            seconda = get_x_y_value(line)
            secondb = get_x_y_value(line_after)
            if compare_lines(pointa, pointb, seconda, secondb):
                sdindex = i - 2
                fdindex = i + 3
                answer = True
                break
        i += 1
    if answer:
        r = sdindex
        while r <= fdindex:
            start_g_code.__delitem__(sdindex)
            r += 1
    return answer

final_output = ''

i = 0

while i < len(start_g_code):
    current_line = start_g_code[i]
    o = i + 1
    if 'G01' in current_line:
        point_one = get_x_y_value(current_line)
        next_line = start_g_code[o]
        line_after_next = start_g_code[o + 1]
        if 'G01' in next_line and 'G01' not in line_after_next:
            point_two = get_x_y_value(next_line)
            if check_for_overlap(point_one, point_two, o):
                final_output = '%s%s' % (final_output, current_line)
            else:
                final_output = '%s%s' % (final_output, current_line)
        else:
            final_output = '%s%s' % (final_output, current_line)
    else:
        final_output = '%s%s' % (final_output, current_line)
    i += 1


def change_x_y_in(change, point):
    x = getattr(point, 'x')
    y = getattr(point, 'y')
    a = change.index('X')
    a += 1
    b = change.index('Y')
    b -= 1
    space = b
    c = change.index('Z')
    b += 2
    c -= 1
    finished = '%s%.4f%s%.4f%s' % (change[:a], x, change[space:b], y, change[c:])
    return finished

edited_g_code = final_output.splitlines(True)


def check_for_connect(pointa, pointb, v):
    sdindex = 0
    fdindex = 0
    answer = False
    while v < len(edited_g_code) - 1:
        line = edited_g_code[v]
        line_after = edited_g_code[v + 1]
        if 'G01' in line and 'G01' in line_after:
            seconda = get_x_y_value(line)
            secondb = get_x_y_value(line_after)
            if should_connect(pointa, pointb, seconda, secondb):
                sdindex = v - 2
                fdindex = v + 3
                if point_equal(pointa, seconda) or point_equal(pointb, seconda):
                    answer = [line_after, line]
                if point_equal(pointa, secondb) or point_equal(pointb, secondb):
                    answer = [line, line_after]
                break
        v += 1
    if answer:
        r = sdindex
        while r <= fdindex:
            edited_g_code.__delitem__(sdindex)
            r += 1
    return answer

super_final_output = ''

was_edited = True
while was_edited:
    was_edited = False
    if len(super_final_output) > 0:
        edited_g_code = super_final_output.splitlines(True)
        super_final_output = ''
    s = 0
    while s < len(edited_g_code):
        current_line = edited_g_code[s]
        t = s + 1
        if 'G01' in current_line:
            first_point = get_x_y_value(current_line)
            next_line = edited_g_code[t]
            line_after_next = edited_g_code[t + 1]
            if 'G01' in next_line and 'G01' not in line_after_next:
                second_point = get_x_y_value(next_line)
                line_to_change = check_for_connect(first_point, second_point, t)
                if line_to_change:
                    f = get_f_value(line_to_change[0])
                    cur_f = get_f_value(current_line)
                    if f == cur_f:
                        if get_f_value(next_line) < f:
                            if point_equal(get_x_y_value(line_to_change[1]), get_x_y_value(current_line)):
                                fudge_line = edited_g_code[s - 2]
                                length = len(super_final_output.splitlines(True))
                                super_final_output = ''.join(super_final_output.splitlines(True)[0:length - 2])
                                super_final_output = '%s%s%s%s%s' % (super_final_output, change_x_y_in(fudge_line, get_x_y_value(line_to_change[0])), 'M12\n', next_line, line_to_change[0])
                            else:
                                super_final_output = '%s%s%s' % (super_final_output, current_line, line_to_change[0])
                        else:
                            if point_equal(get_x_y_value(line_to_change[1]), get_x_y_value(current_line)):
                                fudge_line = edited_g_code[s - 2]
                                length = len(super_final_output.splitlines(True))
                                super_final_output = ''.join(super_final_output.splitlines(True)[0:length - 2])
                                super_final_output = '%s%s%s%s%s' % (super_final_output, change_x_y_in(fudge_line, get_x_y_value(line_to_change[0])), 'M12\n', line_to_change[0], next_line)
                            else:
                                super_final_output = '%s%s%s' % (super_final_output, current_line, line_to_change[0])
                    else:
                        if point_equal(get_x_y_value(line_to_change[1]), get_x_y_value(current_line)):
                            fudge_line = edited_g_code[s - 2]
                            length = len(super_final_output.splitlines(True))
                            super_final_output = ''.join(super_final_output.splitlines(True)[0:length - 2])
                            super_final_output = '%s%s%s%s%s' % (super_final_output, change_x_y_in(fudge_line, get_x_y_value(next_line)), 'M12\n', next_line, line_to_change[0])
                        else:
                            super_final_output = '%s%s%s' % (super_final_output, current_line, line_to_change[0])
                    edited_g_code.__delitem__(t)
                    was_edited = True
                else:
                    super_final_output = '%s%s' % (super_final_output, current_line)
            else:
                super_final_output = '%s%s' % (super_final_output, current_line)
        else:
            super_final_output = '%s%s' % (super_final_output, current_line)
        s += 1

save_and_open(super_final_output)
