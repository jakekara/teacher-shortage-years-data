INF=data/raw/shortage-list.txt
OUTF=data/raw/shortage-list-ascii.txt
# iconv -f utf-8 -t utf-8 -c $INF > $OUTF
iconv -f ascii -t utf-8 -c $INF > $OUTF
