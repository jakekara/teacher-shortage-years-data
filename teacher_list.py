#
# teacher-list.py
# create a more ugseful data structure for teacher shortage list data
#
#
#

#!/usr/bin/env python

from __future__ import print_function
import codecs, re, json, sys
import pandas as pd
import us                       # for state names



INFILE="data/raw/shortage-list-ascii.txt"
BILINGUAL_TERMS = ["BILINGUAL","TESOL","ESOL","TESOL"]
STATELIST = map(lambda x: x.name.upper(), us.states.STATES)

lines = None                      # cache of line list

#
# get_text - get the teacher shortage list as a list of lines
#
def get_text():
    global lines
    
    if lines is None: 
        lines = map(lambda x: x.strip(),
                    codecs.open(INFILE,encoding="UTF-8").read().split("\n"))
    return lines

#
# get_iter - get the lsit of lines as an iterable
#
def get_iter():
    return iter(get_text())

#
# stateline - determine if the line is a state name
#    notes: returns use.states.state object or None
#
def stateline( line ):
    return us.states.lookup( line.strip() )

#
# is_state - return True of False if string is a state
#
def is_state( line ):
    # return stateline( line ) is not None
    return line in STATELIST


def is_year( line ):
    return re.match(r'[0-9]{4}', line) # and len(line.strip()) == 8

def end_year( line ):
    return line == "AMERICAN SAMOA"
    return False
    # return re.match(r'[0-9]{4}', line) and len(line.strip()) != 8

def is_year_range( line ):
    return re.match(r'[0-9]{8} .+ [0-9]{8}', line) is not None

def expand_years_dict( obj ):

    ret = obj.copy()

    # print ("before", ret, file=sys.stdout)
    
    for y in ret.keys():
        if ret[y] is None:
            # print( y, ret[y], "is None", file=sys.stdout )
            continue
        if not is_year_range( y ):
            # print( y, "is not year range", file=sys.stdout )
            continue

        new_years = expand_year( y )
        val = ret[y]
        # print ("Expanding ", y, " with val", val,  " to ",
        #        new_years, file=sys.stdout )
        
        for new_year in new_years:
            if new_year in ret.keys()\
               and ret[new_year] is not None\
               and ret[new_year] != ret[y]:
                print("expand year collision! ",
                      ret["state"],
                      y,
                      new_year,
                      ret[y],
                      # json.dumps(ret, indent=2),
                      file=sys.stdout)
                ret[y] = None   # blank out errors
                # raise Exception("expand year collision! ",
                #                 ret[y],
                #                 new_year,
                #                 json.dumps(ret, indent=2))

            ret[new_year] = ret[y]

    # print ("after", ret, file=sys.stdout)
            
    return ret

#
# regroup - group lines by state, year headings
#
def regroup():
    ret = {}                    # return value data structure
    
    liter = get_iter()

    lines = get_text()
    state = None
    year = None
    all_cats = []
    for line in lines:
        if is_state( line ):
            # print (line)
            state = line
            if state not in ret:
                ret[state] = {}
                
        elif is_year( line ):
            year = line
            # print ("Year: " + line)
            if year not in ret[state]:
                ret[state][year] = {}
            elif end_year( line ):
                year = None
                continue
        else:
            if line not in all_cats:
                all_cats.append(line)
            if state is None or year is None:
                continue
            if year not in ret[state]:
                ret[state][year] = {line: True }
            else:
                ret[state][year][line] = True

    return all_cats, ret



#
# make_df - make pandas dataframe from object returned by regroup
#
def make_df( ):

    all_cats, obj = regroup()
    rows = []
    for state in obj.keys():
        # print (state)
        for year in obj[state].keys():
            # print ("\t" + year)
            row = {
                "state":state,
                "year":year
            }
            for cat in obj[state][year].keys():
                # print ("\t\t" + cat)
                row[cat] = obj[state][year][cat]
            for cat in all_cats:

                if cat not in row:
                    row[cat] = False
            rows.append(row)

    return pd.DataFrame(rows)
    

def category_year( arr, search_terms ):

    for cat in arr:
        for term in search_terms:
            if term.upper() in cat.upper():
                return True
    return False

def category_years_df( search_terms ):

    all_cats, obj = regroup()

    rows = []
    all_years = []

    for state in obj.keys():
        row = {
            "state": state,
        }

        for year in obj[state]:
            if year not in all_years:
                all_years.append( year )
            if category_year( obj[state][year], search_terms ):
                row[year] = True
            else:
                row[year] = False
                
        rows.append( row )

    # for year in all_years:
    #     for row in rows:
    #         if year not in row:
    #             row[year] = None


    new_rows = []
    for row in rows:
        new_rows.append( expand_years_dict ( row ))


    df =  pd.DataFrame( new_rows )
    cols = list(df.columns)
    cols.remove("state")
    cols = ["state"] + cols
    return df[cols]
    
def states_df():

    df = make_df( )
    cols = list(df.columns)
    cols.remove("state")
    cols.remove("year")
    cols = ["state","year"] + cols
    return df[cols]

def syear( year_int ):
    return str(year_int) + str( year_int + 1 )

def year ( syear ):
    return int( syear[:4] )

def start_syear( yearline ):
    return int( yearline[:4] )

def end_syear( yearline ):
    return int( yearline[-8:-4] )

def expand_year( yearstr):

    if not is_year_range( yearstr ):
        return None

    first_year = start_syear( yearstr )
    last_year = end_syear ( yearstr )

    return map(syear, range( first_year, last_year + 1 ) )

print ( expand_year( "19992000 through 20122013" ) )

    
            
    
