from shutil import copyfile
import re


# excepts a def file from the last floorplanning stage of openlane
d_file = open('10-pdn.def', 'r').read()

# Define some helper functions
# Some are derived from https://github.com/google/skywater-pdk/pull/185

stripe_no=0


def find_highest_xy_match(matchobj, r_index):
    res_i=0
    i=0
    lowest_value = None
    for match in matchobj:
        if (lowest_value==None or int(match[r_index]) > lowest_value):
            lowest_value = int(match[r_index])
            res_i = i
        i=i+1

    return res_i

def find_lowest_xy_match(matchobj, r_index):
    res_i=0
    i=0
    lowest_value = None
    for match in matchobj:
        if (lowest_value==None or int(match[r_index]) < lowest_value):
            lowest_value = int(match[r_index])
            res_i = i
        i=i+1

    return res_i

def remove_pgn_striped(text, net_name):
    find    = r'(    - ' + net_name + r'(\s|.\w+).*?\+ FIXED \( (\-*\w+) (\-*\w+) \) N \+ LAYER met4 .*? ;\n)'
    vert_stripes = re.findall(find, text)
    most_right_vertical_stripe  = find_highest_xy_match(vert_stripes, 2) 
    most_left_vertical_stripe = find_lowest_xy_match(vert_stripes, 2)  

    find    = r'(    - ' + net_name + r'(\s|.\w+).*?\+ FIXED \( (\-*\w+) (\-*\w+) \) N \+ LAYER met5 .*? ;\n)'
    horiz_stripes = re.findall(find, text)
    highest_horizontal_stripe = find_highest_xy_match(horiz_stripes, 3) 
    lowest_horizontal_stripe = find_lowest_xy_match(horiz_stripes, 3)  

    replace = vert_stripes[most_right_vertical_stripe][0] + vert_stripes[most_left_vertical_stripe][0] \
            + horiz_stripes[highest_horizontal_stripe][0] + horiz_stripes[lowest_horizontal_stripe][0]

    find    =   r'((    - ' + net_name + r' \+ NET .*? \+ LAYER met4 .*? ;\n)' \
            +   r'(.|\n)*?' \
            +   r'(    - ' + net_name + r'.\w+ .*? \+ LAYER met4 .*? ;\n    - ' + net_name + r'.\w+ .*? \+ LAYER met5 .*? ;\n)' \
            +   r'(    - ' + net_name + r'.\w+ .*? \+ LAYER met5 .*? ;\n)*)' 

    pins_removed = len(vert_stripes) + len(horiz_stripes) - 8

    return (re.sub(find, replace, text), pins_removed)

def edit_pin_count(text, removed_pins):
    find    = r'PINS (\w+) ;\n'
    origig_pin_count = int(re.findall(find, text)[0])
    new_pin_count = origig_pin_count - removed_pins
    return re.sub(find, ('PINS ' + str(new_pin_count) + ' ;\n'), text)

def remove_m1_follow_pins(text):
    find    = r'(      NEW met1 480 \+ SHAPE FOLLOWPIN .*?\)\n)'
    text= re.sub(find, '', text)
    # There is one followpin stripe at last position....
    find    = r'(\n\s*NEW met1 480 \+ SHAPE FOLLOWPIN .*?\) ;\n)'
    return re.sub(find, ' ;\n', text)


def remove_m3_m2_m1_vias(text):
    find    = r'((      \+ ROUTED)( met3 0 \+ SHAPE STRIPE \( \-?\w+ \-?\w+ \) via3_3000x480\n)' \
            + r'(\n|.)*?\n' \
            + r'(      NEW met4 0 \+ SHAPE STRIPE \( \-?\w+ \-?\w+ \) via4_3000x3000\n))'
    replace = r'\2\n\5'
    text = re.sub(find, replace, text)
    # there will be a single + ROUTED line which will be fixed later
    # but it needs to be made uniformly for all pg nets to make next steps easier
    find    = r'((      \+ ROUTED) (met4 0 \+ SHAPE STRIPE \( \-?\w+ \-?\w+ \) via4_3000x3000\n))'
    replace = r'\2\n      NEW \3'
    return re.sub(find, replace, text)

def __find_corner_vias(vias):
    # Find largest and smalest x and ycoordinate
    largest_xc = None
    largest_xc_i = 0
    largest_yc = None
    largest_yc_i = 0
    smallest_xc = None
    smallest_xc_i = 0
    smallest_yc = None
    smallest_yc_i = 0

    i=0
    for via in vias:
        # indexes: 0= whole line, 2=x, 3=y
        if (largest_xc==None or largest_xc < int(via[2])):
            largest_xc=int(via[2]); largest_xc_i=i; 

        if (smallest_xc==None or smallest_xc > int(via[2])):
            smallest_xc=int(via[2]); smallest_xc_i=i; 

        if (largest_yc==None or largest_yc < int(via[3])):
            largest_yc=int(via[3]); largest_yc_i=i; 

        if (smallest_yc==None or smallest_yc > int(via[3])):
            smallest_yc=int(via[3]); smallest_yc_i=i; 
        i = i+1

    # vias[0][1] = white space

    # top right corner
    corner_vias =   vias[0][1]  + "NEW met4 0 + SHAPE STRIPE ( " \
                                + str(largest_xc) + " " + str(largest_yc) \
                                + " ) via4_3000x3000\n"
    # top left corner
    corner_vias =   corner_vias + vias[0][1] + "NEW met4 0 + SHAPE STRIPE ( " \
                                + str(smallest_xc) + " " + str(largest_yc) \
                                + " ) via4_3000x3000\n"

    # bottom right corner
    corner_vias =   corner_vias + vias[0][1]  + "NEW met4 0 + SHAPE STRIPE ( " \
                                + str(largest_xc) + " " + str(smallest_yc) \
                                + " ) via4_3000x3000\n"
    # bottom left corner
    corner_vias =   corner_vias + vias[0][1] + "NEW met4 0 + SHAPE STRIPE ( " \
                                + str(smallest_xc) + " " + str(smallest_yc) \
                                + " ) via4_3000x3000\n"
    return corner_vias

def remove_stripe_ring_vias(text):
    # all vias are between m4 and m5, "via4"
    find    = r'(\n\s*\+ ROUTED\n'\
            + r'((\s*NEW met4 0 \+ SHAPE STRIPE \( (\-?\w+) (\-?\w+) \) via4_3000x3000\n){7,}))'
    via_groups = re.findall(find, text)
    for group in via_groups:
        vias = group[1]
        # Find all Coordinates
        find_c = r'((\s*)NEW met4 0 \+ SHAPE STRIPE \( (\-?\w+) (\-?\w+) \) via4_3000x3000\n)'
        via_c = re.findall(find_c, vias)
        # find all corner vias of each pg net
        corner_visas = __find_corner_vias(via_c)
        replace = "\n" + via_c[0][1] + "+ ROUTED\n" + corner_visas
        # only replace this once, otherwise the following groups are not replaced correctly!
        text = re.sub(find, replace, text, count=1)

    # fix the floating "+ ROUTER\n"
    find    = r'((\s*\+ ROUTED)\n'\
            + r'\s*NEW (met4 0 \+ SHAPE STRIPE \( \-?\w+ \-?\w+ \) via4_3000x3000\n))'
    replace = r'\2 \3'
    text = re.sub(find, replace, text)

    return text

def remove_stripe_special_net_match(matchobj):
    
    header = matchobj.group(2)
    white_space = matchobj.group(3)
    # do not delete metal stripes of the ring

    # met4 are vertical stripes
    vertical_striped = matchobj.group(7)
    # met5 are hoizontal stripes
    horizontal_striped = matchobj.group(5)

    # Find most left/right stripe of vertical stripes
    find_stripes = r'(NEW met4 3000 \+ SHAPE STRIPE \( (\-?\w+) (\-?\w+) \) \( \-?\w+ \-?\w+ \))'
    vert_strip_matches = re.findall(find_stripes, vertical_striped)
    right_stripe = vert_strip_matches[find_highest_xy_match(vert_strip_matches, 1)][0]
    left_stripe = vert_strip_matches[find_lowest_xy_match(vert_strip_matches, 1)][0]

    # Find most left/right stripe of vertical stripes
    find_stripes = r'(NEW met5 3000 \+ SHAPE STRIPE \( (\-?\w+) (\-?\w+) \) \( \-?\w+ \-?\w+ \))'
    hori_strip_matches = re.findall(find_stripes, horizontal_striped)
    top_stripe = hori_strip_matches[find_highest_xy_match(hori_strip_matches, 2)][0]
    bottom_stripe = hori_strip_matches[find_lowest_xy_match(hori_strip_matches, 2)][0]

    replace = header  + white_space + top_stripe + "\n" + white_space + bottom_stripe + "\n" + white_space + right_stripe + "\n" + white_space + left_stripe + " ;\n"
    return replace

def remove_stripe_special_net(text):
    find    = r'((\s*- \w+ \( PIN .*?\n' \
            + r'(\s*)\+ ROUTED .*\n\s+NEW met4(.|\n)*?\n)' \
            + r'((\s*NEW met5 3000 .*?\n)+)' \
            + r'((\s*NEW met4 3000 .*?\n)+))'
    return re.sub(find, remove_stripe_special_net_match, text)

# Remove all pg stripes over the core, but not the core ring
pins_removed=0
d_file, p_rm = remove_pgn_striped(d_file, 'vccd1')
pins_removed = pins_removed + p_rm 
d_file, p_rm = remove_pgn_striped(d_file, 'vssd1')
pins_removed = pins_removed + p_rm 
d_file, p_rm = remove_pgn_striped(d_file, 'vccd2')
pins_removed = pins_removed + p_rm 
d_file, p_rm = remove_pgn_striped(d_file, 'vssd2')
pins_removed = pins_removed + p_rm 
d_file, p_rm = remove_pgn_striped(d_file, 'vdda1')
pins_removed = pins_removed + p_rm 
d_file, p_rm = remove_pgn_striped(d_file, 'vssa1')
pins_removed = pins_removed + p_rm 
d_file, p_rm = remove_pgn_striped(d_file, 'vdda2')
pins_removed = pins_removed + p_rm 
d_file, p_rm = remove_pgn_striped(d_file, 'vssa2')
pins_removed = pins_removed + p_rm 

# Since some Pins have been removed, the Pin count has to be changed as well
d_file = edit_pin_count(d_file, pins_removed)

# Remove all pg_cell connection stripes 
d_file = remove_m1_follow_pins(d_file)

# remove stripe via connections with cell pg stripes
# all contained on met 3,2 and 1
d_file = remove_m3_m2_m1_vias(d_file)

# remove all Stripe-Ring vias
d_file = remove_stripe_ring_vias(d_file)

# remove all Stripe Special nets on metal 4 and metal 5
d_file = remove_stripe_special_net(d_file)


with open('outputs/user_project_wrapper.def','w') as write_file:
    write_file.write(d_file)




















def fix_related_pin_for_pg_pin(text, pg_pin, related_pin, new_pin):
    find    = r'(pg_pin \(\"' + pg_pin + r'\"\) \{\s*\n(.|\n)*?\s+' + related_pin + r' : \")\w+(\";)\n'
    replace = r'\1' + new_pin + r'\3' + '\n'
    return re.sub(find, replace, text)

def fix_related_pin_for_pin(text, pg_pin, related_pin, new_pin):
    find    = r'(pin \(\"' + pg_pin + r'\"\) \{\s*\n(\s*\w+ : \"\w+";\n){1,4}\s+' + related_pin + r' : \")\w+(\";)\n'
    replace = r'\1' + new_pin + r'\3' + '\n'
    return re.sub(find, replace, text)

def fix_missing_pg_pin(text, cell_name, pg_pin, attributes, insert_after_pg_pin=None):
    find    = r'(cell \(\"' + cell_name + r'.*\"\) \{\s*\n)'
    if insert_after_pg_pin != None:
        find    = find + r'(((.|\n)*?)(\n(\s*)pg_pin \(\"' + insert_after_pg_pin + r'\"\) \{\s*\n(.|\n)*?\n\s*\}))'
        replace = r'\1\2\n\6'
        tab = r'\6'
    else:
        find    = find + r'(\s*)'
        replace = r'\1\2\n'
        tab = r'\2'

    replace = replace + 'pg_pin ("' + pg_pin + '") {\n'

    for attr_key, attr_value in attributes.items():
        replace = replace + tab + '    ' + attr_key + ' : "' + attr_value + '";\n'

    replace = replace + tab + '}'

    return re.sub(find, replace, text)

    #find    = r'(pin \(\"' + pg_pin + r'\"\) \{\s*\n(\s*\w+ : \"\w+";\n){1,4}\s+' + related_pin + r' : \")\w+(\";)\n'
    #replace = r'\1' + new_pin + r'\3' + '\n'
    #return re.sub(find, replace, text, re.DOTALL)