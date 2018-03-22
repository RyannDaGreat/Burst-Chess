init='''♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖
♙ ♙ ♙ ♙ ♙ ♙ ♙ ♙
· · · · · · · ·
· · · · · · · ·
· · · · · · · ·
· · · · · · · ·
♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟
♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜'''
#
vacant ='·'
black='♙♖♘♗♕♔'
white='♟♜♞♝♛♚'
pawn  ='♟♙'
rook  ='♜♖'
knight='♞♘'
bishop='♝♗'
king  ='♚♔'
queen ='♛♕'
#
def group(*g):#g is vararg of strings
	from itertools import product#cartesian product
	return {x:y for x,y in product(''.join(g),g)if x in y}
piece   =group(pawn,rook,knight,bishop,king,queen)#{'♔':king,'♟':pawn,'♚':king, ... }
color   =group(black,white)#{'♔':black,'♘':black,'♚':white, ... }
value   ={pawn:1,rook:5,knight:3,bishop:3,king:100,queen:9}
opponent={white:black,black:white}
#
def b2m(b):#board to matrix (make it mutable)
    return [x.split(' ')for x in b.split('\n')]
def m2b(m):#matrix to board (make it immutable)
    return '\n'.join(' '.join(x)for x in m)
def move(b,x0,y0,x1,y1):#one-based from the bottom left
    m=b2m(b)
    m[-y1][x1-1]=p=m[-y0][x0-1]
    assert p in piece,repr(p)+' is not a piece'
    m[-y0][x0-1]=vacant
    if p in pawn and y1 in{1,8}:#Not supported: promoting to non-queen
    	m[-y1][x1-1],=set(queen)&set(color[p])#promote pawn to queen if pawn in a back row
    return m2b(m)
def flipb(b):#flip board:black/white's board positions
    return m2b(reversed([reversed(x)for x in b2m(b)]))
def flipm(*m):#flip move, *m in form x0,y0,x1,y1
	return (9-x for x in m)
def score(b,c):#the total value of all color c's pieces on board b
    return sum(value[piece[x]]for x in b if x in c)
def legal(b,x0,y0,x1,y1):
	#Not supported: castling, en-passant
	m=b2m(b)
	p0=m[x0][y0]#piece before
	if p0 in black:
		m,x0,y0,x1,y1=b2m(flipb(b)),*flipm(x0,y0,x1,y1)#flip everything to make life easier
	p1=m[x1][y1]#piece after
	if p0 in pawn:
		if abs(x0-x1)>1:#Invalid horizontal movement
			return False
		elif x0==x1:#Not capturing a piece
			if y0==2 and y1==4:return p1 is vacant and m[x0][3] is vacant#Moving forward by 2
			elif y1==y0+1:     return p1 is vacant                       #Moving forward by 1
			else:              return False                              #Invalid move
		else:#Capturing a piece
			return y1==y0+1 and p1 in opponent[color[p0]]
	elif p0 in rook:
		if (x0==x1)==(y0==y1):#Either didn't move, or moved both horizontally and vertically
			return False
		elif x0==x1:#We moved on y axis
			x=x0=x1
			for y in range(y0,y1)[1:]:#make sure path BETWEEN 0 and 1 is vacant
				if m[x][y] is not vacant:
					return False
			return p1 in vacant+opponent[color[p0]]#end must be opponent piece or e







