#TAG Chess AI
init='''
♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖
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
    b=b[1:]#get rid of the newline prefix
    return [x.split(' ')for x in b.split('\n')]
def m2b(m):#matrix to board (make it immutable)
    return '\n'+'\n'.join(' '.join(x)for x in m)
def move(b,x0,y0,x1,y1):#one-based from the bottom left
    assert legal(b, x0, y0, x1, y1),'illegal move'
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
def legal(b,x0,y0,x1,y1,print=identity):
    #Not supported: castling, en-passant
    m=b2m(b)
    if not 1<=x0<=8 or not 1<=y0<=8 or not 1<=x1<=8 or not 1<=y1<=8 or x0==x1 and y0==y1:#0 or 1 is off the board or piece didn't move
        print('Out of bounds or no movement')
        return False
    p0=m[-y0][x0-1]#piece before
    if p0 in black:
        m,x0,y0,x1,y1=b2m(flipb(b)),*flipm(x0,y0,x1,y1)#flip everything to make life easier
    try:
        p1=m[-y1][x1-1]#piece after
    except:
        print(-y1,x1-1)
        print(m)
        assert False,'Error?'
    Δ={abs(x1-x0),abs(y1-y0)}
    if p0 in queen:#Queen can act as either bishop or rook
        print('Queen: Δ='+str(Δ))
        if 0 in Δ   :p0,=set(color[p0])&set(rook)
        elif len(Δ)==1:p0,=set(color[p0])&set(bishop)
        else:print('Queen neither acting as rook nor bishop, Δ='+str(Δ));return False
    if p0 in pawn:
        print('Pawn')
        if abs(x0-x1)>1:#Invalid horizontal movement
            print('Pawn cannot move horizontal')
            return False
        if x0==x1:#Not capturing a piece
            if y0==2 and y1==4:return p1 is vacant and m[-3][x0-1] is vacant#Move forward twice
            if y1==y0+1:       return p1 is vacant                          #Move forward once
            return False                                                    #Invalid move
        return y1==y0+1 and p1 in opponent[color[p0]]#Capturing a piece
    if p0 in rook:
        print('Rook')
        if x0==x1:#We moved on y axis
            x,={x0,x1}
            for y in range(min(y0,y1),max(y0,y1))[1:]:#make sure path BETWEEN 0 and 1 is vacant
                if m[-y][x-1] is not vacant:return False
            return p1 in vacant+opponent[color[p0]]#end must be opponent piece or vacant
        if y0==y1:#We moved on x axis
            y,={y0,y1}
            for x in range(min(x0,x1),max(x0,x1))[1:]:#make sure path BETWEEN 0 and 1 is vacant
                if m[-y][x-1] is not vacant:return False
            return p1 in vacant+opponent[color[p0]]#end must be opponent piece or vacant
        return False
    if p0 in knight:
        print('Knight')
        if not Δ=={1,2}:return False
        return p1 in vacant+opponent[color[p0]]
    if p0 in bishop:
        print('Bishop')
        if len(Δ)>1:return False#Not an equal difference
        Δ=Δ.pop()
        assert Δ,'Internal logic error: Piece should be guarenteed to move'
        for _ in range(Δ-1):
            x0+=1 if x0<x1 else -1
            y0+=1 if y0<y1 else -1
            if m[-y0][x0-1] is not vacant:return False#Must be clear path to target
        return p1 in vacant+opponent[color[p0]]
    if p0 in king:
        print('King')
        return Δ<={0,1} and p1 in vacant+opponent[color[p0]]
    print('Piece not recognized: '+repr(p0))
    return False
def moves(b,x,y):
    #Returns the set of all possible resulting legal boards from moving that piece
    p=b2m(b)[-y][x-1]
    Δ=set()#set of different movements to try 
    r=set(range(-7,8))#max possible movement range on the board
    if p in pawn        :Δ|={(0,1),(0,2),(1,1),(-1,1),(0,-1),(0,-2),(1,-1),(-1,-1)}
    if p in rook  +queen:Δ|={(0,n)for n in r}|{( n,0)for n in r}
    if p in bishop+queen:Δ|={(n,n)for n in r}|{(-n,n)for n in r}
    if p in knight      :Δ|={(1,2),(1,-2),(-1,2),(-1,-2),( 2,1),( 2,-1),(-2, 1),(-2,-1)}
    if p in king        :Δ|={(1,0),(1, 1),( 0,1),(-1, 1),(-1,0),(-1,-1),( 0,-1),( 1,-1)}
    out=set()
    for Δx,Δy in Δ:
        args=b,x,y,x+Δx,y+Δy
        if legal(*args):
            yield move(*args)#it's safe to assume every element is unique
def shuffled(l):
    from random import shuffle
    l=list(l)+[]
    shuffle(l)
    return l
def all_moves(b,c):#board,color
    out=set()
    m=b2m(b)
    for x in shuffled(range(1,9)):
        for y in shuffled(range(1,9)):
            if m[-y][x-1] in c:
                for move in moves(b,x,y):
                    if move not in out:
                        yield move
                        out|={move}
def all_n_moves(b,c,n):
    #Up to n moves
    out={b}
    for _ in range(n):
        new_out=out|set()
        for x in out:
            for move in all_moves(x,c):
                if move not in new_out:
                    yield move#using yield is ABSOLUTELY nessecary for performance! Without it, evaluating can take foorrreeevveerrr...like feeling the FULL blunt hit of the combinatorial explostion blah blah u get it right?  yield actually pauses the code here until it's used later'
                    new_out|={move}
        out=new_out
def advantage(b,c):
    return score(b,c)-score(b,opponent[c])
#
def think_1(b,c,bad=9999):
    ba=-9999#*1+advantage(b,c)#biggest advantage seen
    for s in search(b,c):#for search-board in search
        a=advantage(s,c)
        if a>ba:
            out=s
            ba=a
        if a>=bad:#The score is too high! Ignore it
            return None,bad
    return out,ba#move where c has most advantage; c's advantage
def think_2(b,c,bad=-9999):
    sa=9999#smallest advantage seen
    for s in search(b,c):#for search-board in search
        _,a=think_1(s,opponent[c],bad=sa)
        if a<sa:
            out=s
            sa=a
        if a<=bad:
            return None,bad
    return out,sa#move where c's opponent has least advantage; c's largest advantage = -(c's opponent's smallest advantage)
def think_3(b,c,bad=9999):
    ba=-9999#biggest advantage seen
    for s in search(b,c):#for search-board in search
        _,a=think_2(s,opponent[c],bad=ba)
        if a>ba:
            out=s
            ba=a
        if a>=bad:
            return None,bad
    return out,ba#move where c's opponent has least advantage; c's largest advantage = -(c's opponent's smallest advantage)
def think_4(b,c,bad=-9999):
    sa=9999#smallest advantage seen
    for s in search(b,c):#for search-board in search
        _,a=think_3(s,opponent[c],bad=sa)
        if a<sa:
            out=s
            sa=a
        if a<=bad:
            return None,bad
    return out,sa#move where c's opponent has least advantage; c's largest advantage = -(c's opponent's smallest advantage)

play=lambda *m:printed(think_4(move(ans,*m),black))[0]
search=lambda b,c:all_n_moves(b,c,1)
#DEMO:
#    ⮤ init
#    ⮤ play(5,2,5,4)
#    ⮤ play(4,2,4,4)
#    ⮤ play(4,4,4,5)
#    ⮤ play(2,1,3,3)
#    ⮤ ...(etc)...