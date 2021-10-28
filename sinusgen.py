#!/usr/bin/env python3

"""
sinusgen v2.32 [27.10.2021] *** by fieserWolF
usage: sinusgen.py [-h] [-cfg CONFIG_FILE] [-show] [-list] [-output OUTPUT_FILE] [-min MINIMUM_VALUE] [-max MAXIMUM_VALUE] [-steps STEPS]
                    [-type TYPE] [-invert] [-offset OFFSET] [-mod MODULO]

This program writes sinus data as bytes into a binary file. If values are greater than 256, two files are written.

optional arguments:
  -h, --help           show this help message and exit
  -cfg CONFIG_FILE     configuration in .json format
  -show                show preview
  -list                list all avaiable sinus types and exit
  -output OUTPUT_FILE  name of binary output file without its suffix
  -min MINIMUM_VALUE   minimum value (0-65535)
  -max MAXIMUM_VALUE   maximum value (0-65535)
  -steps STEPS         amount of bytes to generate, values below 5 cause an error with some sinus-types
  -type TYPE           sinus type, see output of --list
  -invert              invert values
  -offset OFFSET       step offset, where to begin
  -mod MODULO          modulo value

Note: All values of a config-file can be overwritten by commandline parameters.

Examples:
    ./sinusgen.py -cfg sinus1.json -show
    ./sinusgen.py -output datafile -min 0 -max 255 -steps 256 -type 1 -invert -offset 20 -mod 8
    ./sinusgen.py -cfg sinus1.json -max 255 -type 10 -show
"""

import sys
import struct
import math
import json
import argparse

import PIL.ImageDraw as ImageDraw
import PIL.Image as Image
import PIL.ImageShow as ImageShow 



PROGNAME = 'sinusgen';
VERSION = '2.32';
DATUM = '27.10.2021';

VIEW_WIDTH  = 800
VIEW_HEIGHT = 600

MAXIMUM_VALUE = 65535

TABLE_SINUS_CALC = (
    ('full sinus',2,1,1,0), #0
    ('half sinus',1,1,1,0), #1
    ('shot',1,2,2,1), #2
    ('boobs',1,3,2,1), #3
    ('small hill, big hill',1,4,2,1), #4
    ('high valleys',1,5,2,1), #5
    ('three hills',1,5,2,2), #6
    ('three irregulars',1,6,2,1), #7
    ('four brothers',8,1,2,1), #8
    ('wave shot',3,2,2,1), #9
    ('zig zag',8,5,2,1), #10
    ('double trouble',4,4,2,1), #11
    ('what the heck',3,8,2,1), #12
    ('landscape',5,4,2,1), #13
    ('two hills',5,3,2,1), #14
    ('whatever',5,2,2,1), #15
    ('the famous Mr Ed',4,5,2,1), #16
    ('curly',7,3,2,1), #17
    ('Oh dear...',3,8,2,1), #18
    ('When will it end?',4,9,2,1), #19
    ('ice cream',4,10,2,1), #20
    ('good grief...',8,2,2,1), #21
    ('nonsense',9,2,2,1), #22
    ('windy',10,2,2,1), #23
    ('one more to go',2,11,2,1), #24
    ('Thanks God it`s over.',11,6,2,1) #25
)

 

buffer=[]

#default values:
user_min    = 0
user_max    = 0
user_steps    = 0
user_invert    = False
user_offset    = 0
user_type    = 0
user_mod    = 0
user_show    = False
user_outname    = 'output'




def _calc_sinus(
    factor1,
    factor2,
    multi1,
    multi2
    ) :
    #print "calc_sinus: factor1=%d, factor2=%d, multi1=%d, multi2=%d" %(factor1, factor2, multi1, multi2)

    
    global buffer
    global user_steps
    global user_offset
    global MAXIMUM_VALUE

    my_buffer = []

    for a in range (0,user_steps+1) :

        sinus1 = (
           (
            (
             (MAXIMUM_VALUE/2)*
             math.sin( (a*math.pi) / (user_steps/factor1) )
            ) + (MAXIMUM_VALUE/2)
           ) *multi1
          )

        sinus2 = (
           (
            (
             (MAXIMUM_VALUE/2)*
             math.sin( (a*math.pi) / (user_steps/factor2) )
            ) + (MAXIMUM_VALUE/2)
           ) *multi2
          )
        
        buffer.append(int(sinus1+sinus2)) 

    #copy my_buffer to buffer starting at the given offset
    buffer = buffer[user_offset:user_steps] + buffer[0:user_offset]

    return None




    


def _scale_values(
    ) :
    global buffer
    global user_min
    global user_max
    global user_invert
    global user_mod
    

    # get maximal und minimal values 
    min_buffer = min(buffer)
        
    # normalize data (set minimal value to 0)
    for a in range(0, len(buffer)) :
        buffer[a] -= min_buffer

    scale_user  = (user_max+1) - user_min   #hack: +1 to avoid that nagging $fe $fe $ff $fe $fe problem...
    scale_buffer = max(buffer) - min(buffer)

    # scale values 
    for a in range(0,len(buffer)) :
        my_value = buffer[a] * scale_user / scale_buffer 

        if (user_invert) :
            buffer[a] = (user_max - my_value)
        else :
            buffer[a] = (my_value + user_min)
            
        #undo the hack... the dirty way
        if (buffer[a] > user_max) : buffer[a] = user_max

        # modulo operation
        buffer[a] = buffer[a] % (user_mod+1)
    
    
    return None



def _write_data(
        filename
    ) :
    
    global user_steps
    global user_max
    
    filename_low   = filename+".bin"
    filename_high   = filename+"-high.bin"
    

    print ("    Opening file \"%s\" for writing..." % filename_low)
    try:
        file_out = open(filename_low , "wb")
    except IOError as err:
        print("I/O error: {0}".format(err))
        return 1

    out_buffer = []
    for b in range(0,len(buffer)) :
        out_buffer.append( int(buffer[b]) & 0b11111111 ) # low    
    file_out.write(bytearray(out_buffer))
    file_out.close()


    if ( user_max > 255) :
        print ("    Opening file \"%s\" for writing high-values..." % filename_high)
        try:
            file_out = open(filename_high , "wb")
        except IOError as err:
            print("I/O error: {0}".format(err))
            return 1

        out_buffer = []
        for b in range(0,len(buffer)) :
            out_buffer.append( int(buffer[b]) >> 8 ) # high    
        file_out.write(bytearray(out_buffer))
        file_out.close()


    print("    done.")
    
    return None


def _draw(
    ) :
    global VIEW_HEIGHT
    global VIEW_WIDTH
    global TABLE_SINUS_CALC
    global user_type
    global user_steps
    global user_max
    global user_min
    global user_steps
    global user_invert
    global user_offset
    global user_mod

    # local variables:
    scale_x = VIEW_WIDTH / len(buffer)
    scale_y = VIEW_HEIGHT / max(buffer)
    draw_data = []
    draw_data.append( (0*scale_x,VIEW_HEIGHT ) )
    draw_data.append( (0*scale_x,VIEW_HEIGHT-(buffer[-1]*scale_y ) ) )

    for a in range(0,len(buffer)) :
        draw_data.append( ((a+1)*scale_x,VIEW_HEIGHT-(buffer[a]*scale_y)) )

    draw_data.append( ((len(buffer))*scale_x,VIEW_HEIGHT ) )


    im = Image.new("RGB", (VIEW_WIDTH, VIEW_HEIGHT), "#000044")
    draw = ImageDraw.Draw(im, 'RGBA')



    #y-axis
    for a in range(0,user_max+1) :
        posx = 0
        posy = VIEW_HEIGHT-(a-1)*scale_y
        if ( (a % 5) == 0 )   : draw.line((posx,posy,VIEW_WIDTH,posy), fill="#004444"); continue
    #x-axis
    for a in range(0,len(buffer)+1) :
        posx = a*scale_x
        posy = VIEW_HEIGHT
        if ( (a % 5) == 0 )   : draw.line((posx,posy,posx,0), fill="#004444"); continue

    #y-axis
    for a in range(0,user_max+1) :
        posx = 0
        posy = VIEW_HEIGHT-(a-1)*scale_y
        if ( (a % 10) == 0 )  : draw.line((posx,posy,VIEW_WIDTH,posy),fill="#008888"); draw.text((0, posy-5), str(a)); continue
    #x-axis
    for a in range(0,len(buffer)+1) :
        posx = a*scale_x
        posy = VIEW_HEIGHT
        if ( (a % 10) == 0 )  : draw.line((posx,posy,posx,0),fill="#008888"); draw.text((posx-5, posy-10), str(a)); continue

    #y-axis
    for a in range(0,user_max+1) :
        posx = 0
        posy = VIEW_HEIGHT-(a-1)*scale_y
        if ( (a % 50) == 0 )  : draw.line((posx,posy,VIEW_WIDTH,posy),fill="#00cccc"); draw.text((0, posy-5), str(a)); continue
    #x-axis
    for a in range(0,len(buffer)+1) :
        posx = a*scale_x
        posy = VIEW_HEIGHT
        if ( (a % 50) == 0 )  : draw.line((posx,posy,posx,0),fill="#00cccc"); draw.text((posx-5, posy-10), str(a)); continue

    #y-axis
    for a in range(0,user_max+1) :
        posx = 0
        posy = VIEW_HEIGHT-(a-1)*scale_y
        if ( (a % 100) == 0 ) : draw.line((posx,posy,VIEW_WIDTH,posy),fill="#00ffff"); draw.text((0, posy-5), str(a)); continue
    #x-axis
    for a in range(0,len(buffer)+1) :
        posx = a*scale_x
        posy = VIEW_HEIGHT
        if ( (a % 100) == 0 ) : draw.line((posx,posy,posx,0),fill="#00ffff"); draw.text((posx-5, posy-10), str(a)); continue



    draw.polygon((draw_data),fill="#aa88ccdd", outline="#8888ffdd")



    #y-axis
    for a in range(0,user_max+1) :
        posx = 0
        posy = VIEW_HEIGHT-(a-1)*scale_y
        if ( (a % 100) == 0 ) : draw.line((posx,posy,posx+40,posy),fill="#ffffff"); draw.text((0, posy-5), str(a)); continue
        if ( (a % 50) == 0 )  : draw.line((posx,posy,posx+30,posy),fill="#cccccc"); draw.text((0, posy-5), str(a)); continue
        if ( (a % 10) == 0 )  : draw.line((posx,posy,posx+20,posy),fill="#888888"); draw.text((0, posy-5), str(a)); continue
        if ( (a % 5) == 0 )   : draw.line((posx,posy,posx+10,posy), fill="#444444"); continue


    #x-axis
    for a in range(0,len(buffer)+1) :
        posx = a*scale_x
        posy = VIEW_HEIGHT
        if ( (a % 100) == 0 ) : draw.line((posx,posy,posx,posy-40),fill="#ffffff"); draw.text((posx-5, posy-10), str(a)); continue
        if ( (a % 50) == 0 )  : draw.line((posx,posy,posx,posy-30),fill="#cccccc"); draw.text((posx-5, posy-10), str(a)); continue
        if ( (a % 10) == 0 )  : draw.line((posx,posy,posx,posy-20),fill="#888888"); draw.text((posx-5, posy-10), str(a)); continue
        if ( (a % 5) == 0 )   : draw.line((posx,posy,posx,posy-10), fill="#444444"); continue

    draw.rectangle(((40-3,5-3),(400,50)), fill="#444444aa", outline="#0000aadd")

    #text
    "%s v%s [%s] *** by WolF"% (PROGNAME, VERSION, DATUM)
    
    text = PROGNAME + " v" +  VERSION + " [" + DATUM + "] *** by WolF\n" \
        + "type " +str(user_type)+ " \"" + TABLE_SINUS_CALC[user_type][0] + "\"\n" \
        + str(user_steps) + " values " +str(user_min)+ "-" +str(user_max)+ ", offset=" +str(user_offset)+ ", modulo=" +str(user_mod)

    if (user_invert) :
        text = text + ", inverted values"
    
    draw.text((40, 5), text)  

    im.show()
    
    return None




def _do_it(
        args
    ) :
        
    global user_min, user_max, user_steps, user_invert, user_offset, user_type, user_mod, user_outname
    global user_show
    global sindata

    if (args.list) :
        _show_sinus_types()
        return None


    if (args.config_file) :
        print ("    Opening config-file \"%s\" for reading..." % args.config_file)
        try:
            file_in = open(args.config_file , "r")
        except IOError as err:
            print("I/O error: {0}".format(err))
            return 1

        config = json.load(file_in)
    #        json_value = json.loads(f.read().decode())
        if (config['min']): user_min = config['min']
        if (config['max']): user_max = config['max']
        if (config['steps']): user_steps = config['steps']
        if (config['type']): user_type = config['type']
        if (config['invert']):
            if (config['invert'] != 0) : user_invert = True
        if (config['offset']): user_offset = config['offset']
        if (config['mod']): user_mod = config['mod']
        if (config['output']): user_outname = config['output']


    if (args.minimum_value): user_min = args.minimum_value
    if (args.maximum_value): user_max = args.maximum_value
    if (args.steps): user_steps = args.steps
    if (args.type): user_type = args.type
    if (args.invert): user_invert = args.invert
    if (args.offset): user_offset = args.offset
    if (args.modulo): user_mod = args.modulo
    if (args.output_file): user_output = args.output_file
    
 
################################################
# sanity check:
    
    if (user_min < 0) :
        print ("  **** value-error: min value is %d, but it should be >0." % user_min )
        return 1
    if (user_min >= user_max) :
        print ("  **** value-error: min value is %d, but it should be <%d (max)." % (user_min, user_max) )
        return 1
    if (user_min > MAXIMUM_VALUE) :
        print ("  **** value-error: min value is %d, but it should be <=%d." %( user_max, MAXIMUM_VALUE) )
        return 1
    if (user_max > MAXIMUM_VALUE) :
        print ("  **** value-error: max value is %d, but it should be <=%d." %( user_max, MAXIMUM_VALUE) )
        return 1
    if (user_max <= user_min) :
        print ("  **** value-error: max value is %d, but it should be >%d (min)." %( user_max, user_min))
        return 1
    if (user_steps <= 0) :
        print ("  **** value-error: steps value is %d, but it should be > 0." % (user_steps))
        return 1
    if (user_type >= len(TABLE_SINUS_CALC)) :
        print ("  **** value-error: sinustype value is %d, but it should be <%d." % (user_type, len(TABLE_SINUS_CALC)))
        return 1
#    if (config['show'] > 1) :
#        print ("  **** config-error: show value is %d, but it should be either 0 or 1." % config['show'])
#        return 1
    if (user_offset >= user_steps) :
        print ("  **** value-error: offset value is %d, but it should be <%d (steps)." % (user_offset, user_steps))
        return 1
#    user_mod = config['mod']
    if (user_mod == 0) :
        print ("    Notice: mod value is %d, disabling modulo feature." % user_mod )
        user_mod = user_max






################################################

    print ("    Config: sinustype %d \"%s\", %d values %d-%d, offset=%d, modulo=%d" %(user_type, TABLE_SINUS_CALC[user_type][0], user_steps, user_min, user_max, user_offset, user_mod) )
    if (user_invert) :
        print ("    Values will be inverted.")

################################################
# calculate sinus

    
    _calc_sinus(
        TABLE_SINUS_CALC[user_type][1],
        TABLE_SINUS_CALC[user_type][2],
        TABLE_SINUS_CALC[user_type][3],
        TABLE_SINUS_CALC[user_type][4]
    )
 
    _scale_values()
  

################################################
# write data to file
    
    _write_data(user_outname)

    if (args.show) : _draw()



def _show_sinus_types() :
    print ('Available sinus types:')
    for a in range(0,len(TABLE_SINUS_CALC)) :
        print ('%2d : "%s"' %(a,TABLE_SINUS_CALC[a][0]) )
    return None


def _main_procedure() :
    print("%s v%s [%s] *** by fieserWolF"% (PROGNAME, VERSION, DATUM))

    #https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(
        description='This program writes sinus data as bytes into a binary file. If values are greater than 256, two files are written.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=''\
        'Note: All values of a config-file can be overwritten by commandline parameters.\n\n'\
        'Examples:\n'\
        '    %s -cfg sinus1.json -show\n'\
        '    %s -output datafile -min 0 -max 255 -steps 256 -type 1 -invert -offset 20 -mod 8\n'\
        '    %s -cfg sinus1.json -max 255 -type 10 -show\n' % (sys.argv[0],sys.argv[0],sys.argv[0])
    )
    
    parser.add_argument('-cfg', dest='config_file', help='configuration in .json format')
    parser.add_argument('-show', dest='show', help='show preview', action='store_true')
    parser.add_argument('-list', dest='list', help='list all avaiable sinus types and exit', action='store_true')
    parser.add_argument('-output', dest='output_file', help='name of binary output file without its suffix')
    parser.add_argument('-min', dest='minimum_value', help='minimum value (0-%d)'%MAXIMUM_VALUE, type=int)
    parser.add_argument('-max', dest='maximum_value', help='maximum value (0-%d)'%MAXIMUM_VALUE, type=int)
    parser.add_argument('-steps', dest='steps', help='amount of bytes to generate, values below 5 cause an error with some sinus-types', type=int)
    parser.add_argument('-type', dest='type', help='sinus type, see output of --list', type=int)
    parser.add_argument('-invert', dest='invert', help='invert values', action='store_true')
    parser.add_argument('-offset', dest='offset', help='step offset, where to begin', type=int)
    parser.add_argument('-mod', dest='modulo', help='modulo value', type=int)
    args = parser.parse_args()

    exitcode = _do_it(args)

    if (exitcode != None) :
        print('Exiting with return code %d.' % exitcode) 
    sys.exit(exitcode)

    """
    try:
        sys.exit(exitcode)
    except SystemExit as e:
        print('Exiting with return code "%s".' % e) 
    """


if __name__ == '__main__':
    _main_procedure()
