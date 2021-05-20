#=========================================================================
# generate_init_def.py
#=========================================================================
# This script takes the last generated def file from the openlane
# floorplan step and removes all stripes and vias accross the core area
# as well as the power/ground cell connections
#
# Author : Maximilian Koschay
# Date   : 17.05.2021


from shutil import copyfile
import re


# excepts a def file from the last floorplanning stage of openlane
d_file = open('10-pdn.def', 'r').read()

# Define some helper functions
# Some are derived from https://github.com/google/skywater-pdk/pull/185

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

# remove out-of-die pgn rings and stripes accross the die, leaving only pins in the IO area
def remove_pgn_stripes_and_ring(text, net_name):


    # Find all vertical pg stripes
    find    = r'(    - ' + net_name + r'(\.\w+)? \+ NET ' + net_name  + r' (\+ SPECIAL \+ .*?)' \
            + r' \+ FIXED \( (\-*\w+) (\-*\w+) \) N' \
            + r' \+ LAYER met4 \( \-?(\w+) \-?(\w+) \) \( \-?(\w+) \-?(\w+) \) \;\n)'
    vert_stripes = re.findall(find, text)

    # remember number of original pins
    pin_count=len(vert_stripes)

    # remove the stripes outside of the die area
    vert_stripes.pop(find_highest_xy_match(vert_stripes, 3))
    vert_stripes.pop(find_lowest_xy_match(vert_stripes, 3)) 

    # Cut and shrink the stripes to leave only the minimal physical IO pins in the IO box
    # Some definitions:
    #   Stripe pin length (how far should it go inside the die area?)
    stripe_pin_length='2400' # As long as the signal io pins
    
 
    # list for the new pins
    new_vert_stripes = []
    # also remember location and width, migth be usefull for stripe generation in innovus?
    vert_stripe_positions_width = []

    # stripe pin generation
    stripe_no=1
    for stripe in vert_stripes:
        # get relevant positions from the original
        # X position
        x_pos = stripe[3]
        # pin width
        rect_start_x_offset = stripe[5]
        rect_end_x_offset = stripe[7]
        # Signal Information
        signal_info = stripe[2]

        # generate top pin
        new_vert_stripes.append('    - ' + net_name + '.vert_t'+ str(stripe_no) \
                                + ' + NET ' + net_name + ' ' +  signal_info \
                                + ' + FIXED ( ' + x_pos + ' 3520000 ) N' \
                                + ' + LAYER met4 ( -' + rect_start_x_offset + ' -' + stripe_pin_length +' )' \
                                + ' ( ' + rect_end_x_offset + ' 0 ) ;\n') 

        # generate bottom pin
        new_vert_stripes.append('    - ' + net_name + '.vert_b'+ str(stripe_no) \
                                + ' + NET ' + net_name + ' ' +  signal_info \
                                + ' + FIXED ( ' + x_pos + ' 0 ) N' \
                                + ' + LAYER met4 ( -' + rect_start_x_offset + ' 0 )' \
                                + ' ( ' + rect_end_x_offset + ' ' + stripe_pin_length + ' ) ;\n') 

        # save stripe position
        vert_stripe_positions_width.append([x_pos, int(rect_start_x_offset) + int(rect_end_x_offset)])
        stripe_no = stripe_no + 1


    # do the same with the horizontal stripes
    find    = r'(    - ' + net_name + r'(\.\w+)? \+ NET ' + net_name  + r' (\+ SPECIAL \+ .*?)' \
            + r' \+ FIXED \( (\-*\w+) (\-*\w+) \) N' \
            + r' \+ LAYER met5 \( \-?(\w+) \-?(\w+) \) \( \-?(\w+) \-?(\w+) \) \;\n)'
    horizontal_stripes = re.findall(find, text)

    # remember number of original pins
    pin_count=pin_count + len(horizontal_stripes)

    # remove the stripes outside of the die area
    horizontal_stripes.pop(find_highest_xy_match(horizontal_stripes,4))
    horizontal_stripes.pop(find_lowest_xy_match(horizontal_stripes,4))

    new_horizontal_stripes = []
    horizontal_stripe_positions_width = []

    stripe_no=1
    for stripe in horizontal_stripes:
        # get relevant positions from the original
        # Y position
        y_pos = stripe[4]
        # pin width
        rect_start_y_offset = stripe[6]
        rect_end_y_offset = stripe[8]
        # Signal Information
        signal_info = stripe[2]

        # generate left pin
        new_horizontal_stripes.append('    - ' + net_name + '.hori_l'+ str(stripe_no) \
                                    + ' + NET ' + net_name + ' ' +  signal_info \
                                    + ' + FIXED ( 0 ' + y_pos + ' ) N' \
                                    + ' + LAYER met5 ( 0 -' + rect_start_y_offset + ' )' \
                                    + ' ( ' + stripe_pin_length + ' ' + rect_end_y_offset + ' ) ;\n') 

        # generate right pin
        new_horizontal_stripes.append('    - ' + net_name + '.hori_r'+ str(stripe_no) \
                                    + ' + NET ' + net_name + ' ' +  signal_info \
                                    + ' + FIXED ( 2920000 ' + y_pos + ' ) N' \
                                    + ' + LAYER met5 ( -'+ stripe_pin_length + ' -' + rect_start_y_offset + ' )' \
                                    + ' ( 0 ' + rect_end_y_offset + ' ) ;\n') 


        # save stripe position
        horizontal_stripe_positions_width.append([y_pos ,int(rect_start_y_offset) + int(rect_end_y_offset)])
        stripe_no = stripe_no + 1

    # replace the whole pin definition block
    replace=''
    for stripe in new_vert_stripes:
        replace = replace + stripe

    for stripe in new_horizontal_stripes:
        replace = replace + stripe

    # find and replace the whole block
    find    =   r'((    - ' + net_name + r' \+ NET .*? \+ LAYER met4 .*? ;\n)' \
            +   r'(.|\n)*?' \
            +   r'(    - ' + net_name + r'.\w+ .*? \+ LAYER met4 .*? ;\n    - ' + net_name + r'.\w+ .*? \+ LAYER met5 .*? ;\n)' \
            +   r'(    - ' + net_name + r'.\w+ .*? \+ LAYER met5 .*? ;\n)*)' 

    # migth be negativ!
    pins_removed = pin_count - len(new_vert_stripes) + len(new_horizontal_stripes)

    return (re.sub(find, replace, text), pins_removed, vert_stripe_positions_width, horizontal_stripe_positions_width)


def edit_pin_count(text, removed_pins):
    find    = r'PINS (\w+) ;\n'
    origig_pin_count = int(re.findall(find, text)[0])
    new_pin_count = origig_pin_count - removed_pins
    return re.sub(find, ('PINS ' + str(new_pin_count) + ' ;\n\n'), text)

def remove_special_nets(text):
    find    = r'(SPECIALNETS \w+ ;\n(\n|.)*?\nEND SPECIALNETS\n)'
    return re.sub(find, '\n', text)


def replace_signal_io_location(matchobj):
    metal_layer = matchobj.group(5)
    #location of pin
    xy_coordinate = [int(matchobj.group(3)), int(matchobj.group(4))]
    # Also xy vectors, but interpreted as offsets from startpoint 'xy_coordinat'
    rect_offset_start = [int(matchobj.group(6)), int(matchobj.group(7))]
    rect_offset_end = [int(matchobj.group(8)), int(matchobj.group(9))]
    
    #print("(" + matchobj.group(1) + "\nCoordinate: (" + str(xy_coordinate) \
    #        +"); Rect_offset_start: (" + str(rect_offset_start)\
    #        + "); Rect_offset_end: (" + str(rect_offset_end) \
    #        + "); layer: " + metal_layer)

    orig_top_y_offset=3521200
    orig_bottom_y_offset=-1200
    orig_left_x_offset=-1200
    orig_right_x_offset=2921200

    # Top/Bottom or Left/Right?
    if metal_layer=="met2":
        #Top or Bottom?
        if xy_coordinate[1]==orig_top_y_offset:
            # remove pin offset
            xy_coordinate[1]=3520000
            # shorten on-die pin length (start y is negative!)
            rect_offset_start[1]=rect_offset_start[1] + (orig_top_y_offset - 3520000)
            # remove off-die metal to avoid offDieMetal DRC violations
            rect_offset_end[1]=0
        
        elif xy_coordinate[1]==orig_bottom_y_offset:
            # remove pin offset
            xy_coordinate[1]=0
            # remove off-die metal to avoid offDieMetal DRC violations
            rect_offset_start[1]=0
            # shorten on-die pin length (end y is positive!)
            rect_offset_end[1]= rect_offset_end[1] + orig_bottom_y_offset

        else:
            raise ValueError("IO pin is not on expected offset of either " + str(orig_top_y_offset) \
                + " or " +  str(orig_bottom_y_offset)+". It is at " + str(xy_coordinate[1]) + "!\n"
                + "DEF file line:\n" + matchobj.group(1))

    elif metal_layer=="met3":
        #right or left?
        if xy_coordinate[0]==orig_right_x_offset:
            # remove pin offset
            xy_coordinate[0]=2920000
            # shorten on-die pin length (start x is negative!)
            rect_offset_start[0]=rect_offset_start[0] + (orig_right_x_offset - 2920000)
            # remove off-die metal to avoid offDieMetal DRC violations
            rect_offset_end[0]=0
        
        elif xy_coordinate[0]==orig_left_x_offset:
            # remove pin offset
            xy_coordinate[0]=0
            # remove off-die metal to avoid offDieMetal DRC violations
            rect_offset_start[0]=0
            # shorten on-die pin length (end y is positive!)
            rect_offset_end[0]= rect_offset_end[0] + orig_left_x_offset

        else:
            raise ValueError("IO pin is not on expected offset of either " + str(orig_top_y_offset) \
                + " or " +  str(orig_bottom_y_offset)+". It is at " + str(xy_coordinate[1]) + "!\n"
                + "DEF file line:\n" + matchobj.group(1))
    else:
        raise ValueError("Not sure what kind of signal IO pin is on " + metal_layer + ". DEF file line:\n" + matchobj.group(1))

    #generate replace line
    replace = matchobj.group(2) \
            + " + PLACED ( " + str(xy_coordinate[0]) + " " + str(xy_coordinate[1]) + " ) N" \
            + " + LAYER " + metal_layer \
            + " ( " + str(rect_offset_start[0]) + " " + str(rect_offset_start[1]) + " )" \
            + " ( " + str(rect_offset_end[0]) + " " + str(rect_offset_end[1]) + " ) ;\n"
    
    #print("Original:    " + matchobj.group(1) + "\nReplacement: " + replace)

    return replace

def fix_signal_io_placement(text):
    #- analog_io[0] + NET analog_io[0] + DIRECTION INOUT + USE SIGNAL + PLACED ( 2921200 1426980 ) N + LAYER met3 ( -3600 -600 ) ( 3600 600 ) ;
    find    = r'\n((\s*- .+? \+ NET .+? \+ USE SIGNAL )' \
            + r'\+ PLACED \( (\-?\w+) (\-?\w+) \) N' \
            + r' \+ LAYER (\w+) \( (\-?\w+) (\-?\w+) \) \( (\-?\w+) (\-?\w+) \) \;)'
    #print(re.findall(find, text))
    return re.sub(find, replace_signal_io_location, text)


d_file, p_rm, list1, list2 = remove_pgn_stripes_and_ring(d_file, 'vccd1')


# Remove all pg stripes over the core, but not the core ring
pins_removed=0
d_file, p_rm, vert_stripes, horiz_stripes = remove_pgn_stripes_and_ring(d_file, 'vccd1')
pins_removed = pins_removed + p_rm 
d_file, p_rm, vert_stripes, horiz_stripes = remove_pgn_stripes_and_ring(d_file, 'vssd1')
pins_removed = pins_removed + p_rm 
d_file, p_rm, vert_stripes, horiz_stripes = remove_pgn_stripes_and_ring(d_file, 'vccd2')
pins_removed = pins_removed + p_rm 
d_file, p_rm, vert_stripes, horiz_stripes = remove_pgn_stripes_and_ring(d_file, 'vssd2')
pins_removed = pins_removed + p_rm 
d_file, p_rm, vert_stripes, horiz_stripes = remove_pgn_stripes_and_ring(d_file, 'vdda1')
pins_removed = pins_removed + p_rm 
d_file, p_rm, vert_stripes, horiz_stripes = remove_pgn_stripes_and_ring(d_file, 'vssa1')
pins_removed = pins_removed + p_rm 
d_file, p_rm, vert_stripes, horiz_stripes = remove_pgn_stripes_and_ring(d_file, 'vdda2')
pins_removed = pins_removed + p_rm 
d_file, p_rm, vert_stripes, horiz_stripes = remove_pgn_stripes_and_ring(d_file, 'vssa2')
pins_removed = pins_removed + p_rm 

# Since some Pins have been removed, the Pin count has to be changed as well
d_file = edit_pin_count(d_file, pins_removed)

# Remove SPECIAL NETS
d_file = remove_special_nets(d_file)

# # Fix IO Pin placement to be on die edge and IO metal only on die
d_file = fix_signal_io_placement(d_file)



with open('outputs/user_project_wrapper.def','w') as write_file:
    write_file.write(d_file)





#=========================================================================
# Deprecated functions and edits
#=========================================================================
# The below edits remove the wohle stripes accross the die area and only
# leave the rings outside of the die
# this brings the problem, that innovus will complay about metal out of
# the die area
# Moreover the positions of the stripes are fixed! So we need to have at
# least have some metal of the stripes as special net inputs!
# With the code this is not fullfilled, since the complete stripes are
# removed 



# Functions:

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

def fix_floating_ROUTED(text):
    find    = r'((      \+ ROUTED)\n\s*NEW (met\w .+?)\n)'
    replace = r'\2 \3\n'
    return re.sub(find, replace, text)

# Executed steps


# # Remove all pg stripes over the core, but not the core ring
# pins_removed=0
# d_file, p_rm = remove_pgn_striped(d_file, 'vccd1')
# pins_removed = pins_removed + p_rm 
# d_file, p_rm = remove_pgn_striped(d_file, 'vssd1')
# pins_removed = pins_removed + p_rm 
# d_file, p_rm = remove_pgn_striped(d_file, 'vccd2')
# pins_removed = pins_removed + p_rm 
# d_file, p_rm = remove_pgn_striped(d_file, 'vssd2')
# pins_removed = pins_removed + p_rm 
# d_file, p_rm = remove_pgn_striped(d_file, 'vdda1')
# pins_removed = pins_removed + p_rm 
# d_file, p_rm = remove_pgn_striped(d_file, 'vssa1')
# pins_removed = pins_removed + p_rm 
# d_file, p_rm = remove_pgn_striped(d_file, 'vdda2')
# pins_removed = pins_removed + p_rm 
# d_file, p_rm = remove_pgn_striped(d_file, 'vssa2')
# pins_removed = pins_removed + p_rm 




# # remove stripe via connections with cell pg stripes
# # all contained on met 3,2 and 1
# d_file = remove_m3_m2_m1_vias(d_file)

# # remove all Stripe-Ring vias
# d_file = remove_stripe_ring_vias(d_file)

# # remove all Stripe Special nets on metal 4 and metal 5
# d_file = remove_stripe_special_net(d_file)

# # Fix Floating ROUTED
# #d_file = fix_floating_ROUTED(d_file)

# Remove all pg_cell connection stripes 
# d_file = remove_m1_follow_pins(d_file)