#!/usr/bin/python3

import sys

FILENAME="battlefield.txt"
#FILENAME="small.txt"

SHIP="1"
SUNK="*"
SUNK_ENEMY="+"
SEE="."
UKNOWN=" "
SURROUNDING="s"
ENEMY="e"

MAX_SHIP_POSITIONS=10

SHIPS=[(2,3),(1,5),(1,4),(1,3),(1,3),(1,2),(1,2)]
#SHIPS=[(1,3),(1,2),(1,2)]

FOUND_51=0
FOUND_41=0
FOUND_32=0
FOUND_31=0
FOUND_21=0

#
# Misc
#

def get_field():
    fd=open(FILENAME, "r")
    line=fd.readline().split(" ")
    SHIP=line[0]
    rounds=int(line[1])
    shots=int(line[2])
    field=[]
    for line in fd:
        field.append(list(line))
    for line in field:
        line.pop()
    return (field, rounds, shots)

def log(s):
    fd=None
    if(rounds==150):
        fd=open("log", "w")
    else:
        fd=open("log", "a")
    print("{0:=2}:{1}".format(150-rounds+1, s), file=fd)

#
# Combinations
#

class TooManyCombinationsException(Exception):
    pass

class SurroundingException(Exception):
    pass

def print_field(field):
    print("   01234567890123", file=sys.stderr)
    i=0
    for line in field:
        print("{0:=2}|".format(i)+"".join(line)+"|", file=sys.stderr)
        i+=1
    print("  ----------------", file=sys.stderr)

def copy_field(field):
    return [list(line) for line in field]

def check_field(field):
    for line in field:
        if SUNK_ENEMY in line:
            return False
    return True

def get_ship_tiles(ship, x, y, o):
    if o:
        ship=(ship[1], ship[0])
    for w in range(ship[0]):
        for h in range(ship[1]):
            yield (x+w, y+h)

def get_surrounding_tiles(ship, x, y, o):
    if o:
        ship=(ship[1], ship[0])
    if x>0 and y>0:
        yield (x-1, y-1)
    if x+ship[0]<FIELD_WIDTH and y>0:
        yield (x+ship[0], y-1)
    if x+ship[0]<FIELD_WIDTH and y+ship[1]<FIELD_HEIGHT:
        yield (x+ship[0], y+ship[1])
    if x>0 and y+ship[1]<FIELD_HEIGHT:
        yield (x-1, y+ship[1])
    if x>0:
        for i in range(ship[1]):
            yield (x-1, y+i)
    if y>0:
        for i in range(ship[0]):
            yield (x+i, y-1)
    if x+ship[0]<FIELD_WIDTH:
        for i in range(ship[1]):
            yield (x+ship[0], y+i)
    if y+ship[1]<FIELD_HEIGHT:
        for i in range(ship[0]):
            yield (x+i, y+ship[1])

def check_position(ship, field, x, y, o):
    if o:
        if x+ship[1]-1>=FIELD_WIDTH or y+ship[0]-1>=FIELD_HEIGHT:
            return False
    else:
        if x+ship[0]-1>=FIELD_WIDTH or y+ship[1]-1>=FIELD_HEIGHT:
            return False
    for tile in get_ship_tiles(ship, x, y, o):
        tile_type=field[tile[1]][tile[0]]
        if tile_type!=UKNOWN and tile_type!=SUNK_ENEMY:
            return False
    return True

def get_positions(ship, field):
    for o in (False, True):
        for y in range(FIELD_HEIGHT):
            for x in range(FIELD_WIDTH):
                if check_position(ship, field, x, y, o):
                    yield (x, y, o)

def get_combinations(field, ships):
    #print(ships)
    if len(ships)==0:
        if check_field(field):
            #print_field(field)
            return [field]
        else:
            return []
    ship_positions=[position for position in get_positions(ships[0], field)]
    #print(len(ship_positions), file=sys.stderr)
    if len(ship_positions)==0:
        return []
    if len(ship_positions)>MAX_SHIP_POSITIONS:
        raise TooManyCombinationsException()
    result=[]
    for position in ship_positions:
        try:
            new_field=insert_ship(field, ships[0], *position)
            result.extend(get_combinations(new_field, ships[1:]))
        except SurroundingException:
            continue
    return result

def insert_ship(field, ship, x, y, o):
    field=copy_field(field)
    for tile in get_ship_tiles(ship, x, y, o):
        field[tile[1]][tile[0]]=ENEMY
    for tile in get_surrounding_tiles(ship, x, y, o):
        if field[tile[1]][tile[0]]==SUNK_ENEMY:
            raise SurroundingException()
        else:
            field[tile[1]][tile[0]]=SURROUNDING
    return field

def get_highest_chance_tile(combinations, field):
    e_max=0
    tile=()
    for y in range(FIELD_HEIGHT):
        for x in range(FIELD_WIDTH):
            e=0
            for c in combinations:
                if c[y][x]==ENEMY:
                    e+=1
            if e>e_max and field[y][x]!=SUNK_ENEMY and field[y][x]!=ENEMY:
                e_max=e
                tile=(x, y)
    return (tile[0], tile[1], e_max)

#
# Coloring
#

def color_surrounding_tiles(field):
    for y in range(FIELD_HEIGHT):
        for x in range(FIELD_WIDTH):
            if field[y][x]==SHIP or field[y][x]==SUNK:
                for tile in ((x+1, y),(x, y+1),(x+1, y+1),(x-1, y),(x, y-1),(x-1, y-1),(x+1, y-1),(x-1, y+1)):
                    if tile[0]>=0 and tile[0]<FIELD_WIDTH and tile[1]>=0 and tile[1]<FIELD_HEIGHT and field[tile[1]][tile[0]]==UKNOWN:
                        field[tile[1]][tile[0]]=SURROUNDING

def get_enemy_ship_position(ship, field):
    for y in range(FIELD_HEIGHT):
        for x in range(FIELD_WIDTH):
            if field[y][x]==SUNK_ENEMY:
                found=True
                try:
                    for i in range(0, ship[1]):
                        for j in range(0, ship[0]):
                            if field[y+j][x+i]!=SUNK_ENEMY:
                                found=False
                                break
                except IndexError:
                    found=False
                if found:
                    yield (x, y, True)
                found=True
                try:
                    for i in range(0, ship[1]):
                        for j in range(0, ship[0]):
                            if field[y+i][x+j]!=SUNK_ENEMY:
                                found=False
                                break
                except IndexError:
                    found=False
                if found:
                    yield (x, y, False)

def color_32(field):
    global FOUND_32, SHIPS
    for ship in get_enemy_ship_position((2,3), field):
        for tile in get_surrounding_tiles((2,3), *ship):
            if field[tile[1]][tile[0]]==UKNOWN:
                field[tile[1]][tile[0]]=SURROUNDING
        for tile in get_ship_tiles((2,3), *ship):
            field[tile[1]][tile[0]]=ENEMY
        FOUND_32+=1
        SHIPS.remove((2, 3))

def color_51(field):
    global FOUND_51, SHIPS
    for ship in get_enemy_ship_position((1,5), field):
        for tile in get_surrounding_tiles((1,5), *ship):
            if field[tile[1]][tile[0]]==UKNOWN:
                field[tile[1]][tile[0]]=SURROUNDING
        for tile in get_ship_tiles((1,5), *ship):
            field[tile[1]][tile[0]]=ENEMY
        FOUND_51+=1
        SHIPS.remove((1, 5))

def check_41(field, x, y, o):
    if o:
        if (x>0 and field[y][x-1]==SUNK_ENEMY) or (x+3<FIELD_WIDTH-1 and field[y][x+4]==SUNK_ENEMY):
            return False
        if (x==0 or field[y][x-1]!=UKNOWN) and (x+3==FIELD_WIDTH-1 or field[y][x+4]!=UKNOWN):
            return True
    else:
        if (y>0 and field[y-1][x]==SUNK_ENEMY) or (y+3<FIELD_HEIGHT-1 and field[y+4][x]==SUNK_ENEMY):
            return False
        if (y==0 or field[y-1][x]!=UKNOWN) and (y+3==FIELD_HEIGHT-1 or field[y+4][x]!=UKNOWN):
            return True
    return FOUND_51

def color_41(field):
    global FOUND_41, SHIPS
    for ship in get_enemy_ship_position((1,4), field):
        if check_41(field, *ship):
            for tile in get_surrounding_tiles((1,4), *ship):
                if field[tile[1]][tile[0]]==UKNOWN:
                    field[tile[1]][tile[0]]=SURROUNDING
            for tile in get_ship_tiles((1,4), *ship):
                field[tile[1]][tile[0]]=ENEMY
            FOUND_41+=1
            SHIPS.remove((1, 4))

def check_31(field, x, y, o):
    if o:
        if (x>0 and field[y][x-1]==SUNK_ENEMY) or (x+2<FIELD_WIDTH-1 and field[y][x+3]==SUNK_ENEMY) or\
            (y>0 and (field[y-1][x]==SUNK_ENEMY or field[y-1][x+1]==SUNK_ENEMY or field[y-1][x+2]==SUNK_ENEMY)) or\
            (y<FIELD_HEIGHT-1 and (field[y+1][x]==SUNK_ENEMY or field[y+1][x+1]==SUNK_ENEMY or field[y+1][x+2]==SUNK_ENEMY)):
            return False
        if (x==0 or field[y][x-1]!=UKNOWN) and (x+2==FIELD_WIDTH-1 or field[y][x+3]!=UKNOWN) and\
            (y==0 or field[y-1][x]!=UKNOWN or field[y-1][x+1]!=UKNOWN or field[y-1][x+2]!=UKNOWN) and\
            (y==FIELD_HEIGHT-1 or field[y+1][x]!=UKNOWN or field[y+1][x+1]!=UKNOWN or field[y+1][x+2]!=UKNOWN):
            return True
    else:
        if (y>0 and field[y-1][x]==SUNK_ENEMY) or (y+2<FIELD_HEIGHT-1 and field[y+3][x]==SUNK_ENEMY) or\
            (x>0 and (field[y][x-1]==SUNK_ENEMY or field[y+1][x-1]==SUNK_ENEMY or field[y+2][x-1]==SUNK_ENEMY)) or\
            (x<FIELD_WIDTH-1 and (field[y][x+1]==SUNK_ENEMY or field[y+1][x+1]==SUNK_ENEMY or field[y+2][x+1]==SUNK_ENEMY)):
            return False
        if (y==0 or field[y-1][x]!=UKNOWN) and (y+2==FIELD_HEIGHT-1 or field[y+3][x]!=UKNOWN) and\
            (x==0 or field[y][x-1]!=UKNOWN or field[y+1][x-1]!=UKNOWN or field[y+2][x-1]!=UKNOWN) and\
            (x==FIELD_WIDTH-1 or field[y][x+1]!=UKNOWN or field[y+1][x+1]!=UKNOWN or field[y+2][x+1]!=UKNOWN):
            return True
    return FOUND_51 and FOUND_41 and FOUND_32

def color_31(field):
    global FOUND_31, SHIPS
    for ship in get_enemy_ship_position((1,3), field):
        if check_31(field, *ship):
            for tile in get_surrounding_tiles((1,3), *ship):
                if field[tile[1]][tile[0]]==UKNOWN:
                    field[tile[1]][tile[0]]=SURROUNDING
            for tile in get_ship_tiles((1,3), *ship):
                field[tile[1]][tile[0]]=ENEMY
            FOUND_31+=1
            SHIPS.remove((1, 3))

def check_21(field, x, y, o):
    if o:
        if (x>0 and field[y][x-1]==SUNK_ENEMY) or (x+1<FIELD_WIDTH-1 and field[y][x+2]==SUNK_ENEMY) or\
            (y>0 and (field[y-1][x]==SUNK_ENEMY or field[y-1][x+1]==SUNK_ENEMY)) or\
            (y<FIELD_HEIGHT-1 and (field[y+1][x]==SUNK_ENEMY or field[y+1][x+1]==SUNK_ENEMY)):
            return False
        if (x==0 or field[y][x-1]!=UKNOWN) and (x+1==FIELD_WIDTH-1 or field[y][x+2]!=UKNOWN) and\
            (y==0 or field[y-1][x]!=UKNOWN or field[y-1][x+1]!=UKNOWN) and\
            (y==FIELD_HEIGHT-1 or field[y+1][x]!=UKNOWN or field[y+1][x+1]!=UKNOWN):
            return True
    else:
        if (y>0 and field[y-1][x]==SUNK_ENEMY) or (y+1<FIELD_HEIGHT-1 and field[y+2][x]==SUNK_ENEMY) or\
            (x>0 and (field[y][x-1]==SUNK_ENEMY or field[y+1][x-1]==SUNK_ENEMY)) or\
            (x<FIELD_WIDTH-1 and (field[y][x+1]==SUNK_ENEMY or field[y+1][x+1]==SUNK_ENEMY)):
            return False
        if (y==0 or field[y-1][x]!=UKNOWN) and (y+1==FIELD_HEIGHT-1 or field[y+2][x]!=UKNOWN) and\
            (x==0 or field[y][x-1]!=UKNOWN or field[y+1][x-1]!=UKNOWN) and\
            (x==FIELD_WIDTH-1 or field[y][x+1]!=UKNOWN or field[y+1][x+1]!=UKNOWN):
            return True
    return FOUND_51 and FOUND_41 and FOUND_32 and FOUND_31==2

def color_21(field):
    global FOUND_21, SHIPS
    for ship in get_enemy_ship_position((1,2), field):
        if check_21(field, *ship):
            for tile in get_surrounding_tiles((1,2), *ship):
                if field[tile[1]][tile[0]]==UKNOWN:
                    field[tile[1]][tile[0]]=SURROUNDING
            for tile in get_ship_tiles((1,2), *ship):
                field[tile[1]][tile[0]]=ENEMY
            FOUND_21+=1
            SHIPS.remove((1, 2))

def color_found_ships(field):
    color_51(field)
    color_41(field)
    color_32(field)
    color_31(field)
    color_21(field)

#
# Torpedos
#

def get_directions_from_tile(field, ox, oy):
    for d in ("u","d","l","r"):
        (l, x, y)=(0, ox, oy)
        while True: 
            if d=="u":
                y-=1
            elif d=="d":
                y+=1
            elif d=="l":
                x-=1
            elif d=="r":
                x+=1
            if not (x>=0 and y>=0 and x<FIELD_WIDTH and y<FIELD_HEIGHT):
                yield (l, ox, oy, d)
                break
            tile=field[y][x]
            if tile==SHIP:
                yield (l, ox, oy, d)
                break
            elif tile==UKNOWN:
                l+=1

def get_directions(field):
    for y in range(FIELD_HEIGHT):
        for x in range(FIELD_WIDTH):
            if field[y][x]==SHIP:
                for d in get_directions_from_tile(field, x, y):
                    if d[0]!=0:
                        yield d

#
# Lines
#

def get_longest_line(field):
    l_max=0
    start_max=()
    end_max=()
    for y in range(FIELD_HEIGHT):
        l=0
        start=(0, y)
        for x in range(FIELD_WIDTH):
            if field[y][x]==UKNOWN:
                l+=1
            
            if field[y][x]!=UKNOWN:
                if l>l_max:
                    l_max=l
                    start_max=start
                    end_max=(x-1, y)
                l=0
                start=(x+1, y)
            elif x==FIELD_WIDTH-1:
                if l>l_max:
                    l_max=l
                    start_max=start
                    end_max=(x, y)
                l=0
                start=(x+1, y)
    for x in range(FIELD_WIDTH):
        l=0
        start=(x, 0)
        for y in range(FIELD_HEIGHT):
            if field[y][x]==UKNOWN:
                l+=1
            
            if field[y][x]!=UKNOWN:
                if l>l_max:
                    l_max=l
                    start_max=start
                    end_max=(x, y-1)
                l=0
                start=(x, y+1)
            elif y==FIELD_HEIGHT-1:
                if l>l_max:
                    l_max=l
                    start_max=start
                    end_max=(x, y)
                l=0
                start=(x, y+1)
    return (start_max, end_max)

#
# Pattern-matching
#

def get_between(field):
    for y in range(FIELD_HEIGHT):
        for x in range(FIELD_WIDTH):
            if field[y][x]==SUNK_ENEMY:
                if x+2<FIELD_WIDTH and field[y][x+2]==SUNK_ENEMY and field[y][x+1]==UKNOWN and \
                    (y==0 or (field[y-1][x]!=SUNK_ENEMY and field[y-1][x+2]!=SUNK_ENEMY)) and \
                    (y==FIELD_HEIGHT-1 or (field[y+1][x]!=SUNK_ENEMY and field[y+1][x+2]!=SUNK_ENEMY)):
                    return (x+1, y)
                if y+2<FIELD_HEIGHT and field[y+2][x]==SUNK_ENEMY and field[y+1][x]==UKNOWN and \
                    (x==0 or (field[y][x-1]!=SUNK_ENEMY and field[y+2][x-1]!=SUNK_ENEMY)) and \
                    (x==FIELD_WIDTH-1 or (field[y][x+1]!=SUNK_ENEMY and field[y+2][x+1]!=SUNK_ENEMY)):
                    return (x, y+1)

def get_skew(field):
    for y in range(FIELD_HEIGHT):
        for x in range(FIELD_WIDTH):
            if field[y][x]==SUNK_ENEMY:
                if y<FIELD_HEIGHT-1:
                    if x<FIELD_WIDTH-1 and field[y+1][x+1]==SUNK_ENEMY:
                        if field[y][x+1]==UKNOWN:
                            return (x+1, y)
                        elif field[y+1][x]==UKNOWN:
                            return (x, y+1)
                    if x>0 and field[y+1][x-1]==SUNK_ENEMY:
                        if field[y][x-1]==UKNOWN:
                            return (x-1, y)
                        elif field[y+1][x]==UKNOWN:
                            return (x, y+1)

def get_corners(field):
    if field[0][0]==SUNK_ENEMY:
        if field[0][1]==SUNK_ENEMY or field[1][0]==SUNK_ENEMY:
            pass
        elif field[0][1]!=UKNOWN:
            return (0, 1)
        elif field[1][0]!=UKNOWN:
            return (1, 0)
    if field[0][FIELD_WIDTH-1]==SUNK_ENEMY:
        if field[0][FIELD_WIDTH-2]==SUNK_ENEMY or field[1][FIELD_WIDTH-1]==SUNK_ENEMY:
            pass
        elif field[0][FIELD_WIDTH-2]!=UKNOWN:
            return (FIELD_WIDTH-1, 1)
        elif field[1][FIELD_WIDTH-1]!=UKNOWN:
            return (FIELD_WIDTH-2, 0)
    if field[FIELD_HEIGHT-1][0]==SUNK_ENEMY:
        if field[FIELD_HEIGHT-2][0]==SUNK_ENEMY or field[FIELD_HEIGHT-1][1]==SUNK_ENEMY:
            pass
        elif field[FIELD_HEIGHT-1][1]!=UKNOWN:
            return (0, FIELD_HEIGHT-2)
        elif field[FIELD_HEIGHT-2][0]!=UKNOWN:
            return (1, FIELD_HEIGHT-1)
    if field[FIELD_HEIGHT-1][FIELD_WIDTH-1]==SUNK_ENEMY:
        if field[FIELD_HEIGHT-2][FIELD_WIDTH-1]==SUNK_ENEMY or field[FIELD_HEIGHT-1][FIELD_WIDTH-2]==SUNK_ENEMY:
            pass
        elif field[FIELD_HEIGHT-1][FIELD_WIDTH-2]!=UKNOWN:
            return (FIELD_WIDTH-1, FIELD_HEIGHT-2)
        elif field[FIELD_HEIGHT-2][FIELD_WIDTH-1]!=UKNOWN:
            return (FIELD_WIDTH-2, FIELD_HEIGHT-1)

def get_single(field):
    for y in range(1, FIELD_HEIGHT-1):
        for x in range(1, FIELD_WIDTH-1):
            if field[y][x]==SUNK_ENEMY:
                if field[y][x-1]==SUNK_ENEMY:
                    if field[y][x+1]==UKNOWN:
                        return (x+1, y)
                elif field[y][x+1]==SUNK_ENEMY:
                    if field[y][x-1]==UKNOWN:
                        return (x-1, y)
                elif field[y-1][x]==SUNK_ENEMY:
                    if field[y+1][x]==UKNOWN:
                        return (x, y+1)
                elif field[y+1][x]==SUNK_ENEMY:
                    if field[y-1][x]==UKNOWN:
                        return (x, y-1)
                elif field[y][x-1]==UKNOWN:
                    return (x-1, y)
                elif field[y][x+1]==UKNOWN:
                    return (x+1, y)
                elif field[y-1][x]==UKNOWN:
                    return (x, y-1)
                elif field[y+1][x]==UKNOWN:
                    return (x, y+1)
    for y in range(1, FIELD_HEIGHT-1):
        if field[y][0]==SUNK_ENEMY:
            if field[y-1][0]==SUNK_ENEMY:
                if field[y+1][0]==UKNOWN:
                    return (0, y+1)
            elif field[y+1][0]==SUNK_ENEMY:
                if field[y-1][0]==UKNOWN:
                    return (0, y-1)
            elif field[y][1]==UKNOWN:
                return (1, y)
            elif field[y-1][0]==UKNOWN:
                return (0, y-1)
            elif field[y+1][0]==UKNOWN:
                return (0, y+1)
        if field[y][FIELD_WIDTH-1]==SUNK_ENEMY:
            if field[y-1][FIELD_WIDTH-1]==SUNK_ENEMY:
                if field[y+1][FIELD_WIDTH-1]==UKNOWN:
                    return (FIELD_WIDTH-1, y+1)
            elif field[y+1][FIELD_WIDTH-1]==SUNK_ENEMY:
                if field[y-1][FIELD_WIDTH-1]==UKNOWN:
                    return (FIELD_WIDTH-1, y-1)
            elif field[y][FIELD_WIDTH-2]==UKNOWN:
                return (FIELD_WIDTH-2, y)
            elif field[y-1][FIELD_WIDTH-1]==UKNOWN:
                return (FIELD_WIDTH-1, y-1)
            elif field[y+1][FIELD_WIDTH-1]==UKNOWN:
                return (FIELD_WIDTH-1, y+1)
    for x in range(1, FIELD_WIDTH-1):
        if field[0][x]==SUNK_ENEMY:
            if field[0][x-1]==SUNK_ENEMY:
                if field[0][x+1]==UKNOWN:
                    return (x+1, 0)
            elif field[0][x+1]==SUNK_ENEMY:
                if field[0][x-1]==UKNOWN:
                    return (x-1, 0)
            elif field[1][x]==UKNOWN:
                return (x, 1)
            elif field[0][x-1]==UKNOWN:
                return (x-1, 0)
            elif field[0][x+1]==UKNOWN:
                return (x+1, 0)
        if field[FIELD_HEIGHT-1][x]==SUNK_ENEMY:
            if field[FIELD_HEIGHT-1][x-1]==SUNK_ENEMY:
                if field[FIELD_HEIGHT-1][x+1]==UKNOWN:
                    return (x+1, FIELD_HEIGHT-1)
            elif field[FIELD_HEIGHT-1][x+1]==SUNK_ENEMY:
                if field[FIELD_HEIGHT-1][x-1]==UKNOWN:
                    return (x-1, FIELD_HEIGHT-1)
            elif field[FIELD_HEIGHT-2][x]==UKNOWN:
                return (x, FIELD_WIDTH-2)
            elif field[FIELD_HEIGHT-1][x-1]==UKNOWN:
                return (x-1, FIELD_HEIGHT-1)
            elif field[FIELD_HEIGHT-1][x+1]==UKNOWN:
                return (x+1, FIELD_HEIGHT-1)

def get_square(field):
    for y in range(FIELD_HEIGHT-1):
        for x in range(FIELD_WIDTH-1):
            if field[y][x]==SUNK_ENEMY and field[y+1][x]==SUNK_ENEMY and field[y][x+1]==SUNK_ENEMY and field[y+1][x+1]==SUNK_ENEMY:
                if x>0 and field[y][x-1]==UKNOWN and field[y+1][x-1]==UKNOWN:
                    return (x-1,y)
                elif x+1<FIELD_WIDTH-1 and field[y][x+2]==UKNOWN and field[y+1][x+2]==UKNOWN:
                    return (x+2,y)
                elif y>0 and field[y-1][x]==UKNOWN and field[y-1][x+1]==UKNOWN:
                    return (x,y-1)
                elif y+1<FIELD_HEIGHT-1 and field[y+2][x]==UKNOWN and field[y+2][x+1]==UKNOWN:
                    return (x,y+2)


def get_implied_enemy(field):
    tile=get_corners(field)
    if tile:
        return tile
    tile=get_skew(field)
    if tile:
        return tile
    tile=get_between(field)
    if tile:
        return tile
    tile=get_single(field)
    if tile:
        return tile
    tile=get_square(field)
    if tile:
        return tile

#
# Funkce main
#

def main(field, rounds, shots):
    try:
        combinations=get_combinations(field, SHIPS)
        tile=get_highest_chance_tile(combinations, field)
        if not tile:
            raise TooManyCombinationsException()
        if tile[2]<len(combinations):
            raise TooManyCombinationsException()
        print("m {0} {1}".format(*tile[:2]))
        log("comb:"+"m {0} {1} {2}".format(*tile))
    except TooManyCombinationsException:
        tile=get_implied_enemy(field)
        if tile:
            print("m {0} {1}".format(*tile))
            log("impl:"+"m {0} {1}".format(*tile))
            return
        if shots>0:
            direction=(0, 0, 0, "O")
            for d in get_directions(field):
                if direction[0]<d[0]:
                    direction=d
            if direction!=(0, 0, 0, "O"):
                print("t {0} {1} {2}".format(*direction[1:]))
                log("torp:"+"t {0} {1} {2} {a}".format(*direction[1:], a=direction[0]))
                return
        line=get_longest_line(field)
        print("m {0} {1}".format((line[0][0]+line[1][0])//2, (line[0][1]+line[1][1])//2))
        log("line:"+"m {0} {1}".format((line[0][0]+line[1][0])//2, (line[0][1]+line[1][1])//2))

(field, rounds, shots)=get_field()

FIELD_WIDTH=len(field[0])
FIELD_HEIGHT=len(field)

color_surrounding_tiles(field)
#print_field(field)
color_found_ships(field)
#print_field(field)

#print("FIELD", file=sys.stderr)
#print_field(field)

if __name__=="__main__":
    main(field, rounds, shots)
