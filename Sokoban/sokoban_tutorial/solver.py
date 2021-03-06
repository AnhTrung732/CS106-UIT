import sys
import collections
import numpy as np
import heapq
import time
import numpy as np
global posWalls, posGoals
class PriorityQueue:
    """Define a PriorityQueue data structure that will be used"""
    def  __init__(self):
        self.Heap = []
        self.Count = 0
        self.len = 0

    def push(self, item, priority):
        entry = (priority, self.Count, item)
        heapq.heappush(self.Heap, entry)
        self.Count += 1

    def pop(self):
        if len(self.Heap) < 1:
            return -1
        (_, _, item) = heapq.heappop(self.Heap)
        return item


    def isEmpty(self):
        return len(self.Heap) == 0

"""Load puzzles and define the rules of sokoban"""

def transferToGameState(layout):
    """Transfer the layout of initial puzzle"""
    layout = [x.replace('\n','') for x in layout]
    layout = [','.join(layout[i]) for i in range(len(layout))]
    layout = [x.split(',') for x in layout]
    maxColsNum = max([len(x) for x in layout])
    for irow in range(len(layout)):
        for icol in range(len(layout[irow])):
            if layout[irow][icol] == ' ': layout[irow][icol] = 0   # free space
            elif layout[irow][icol] == '#': layout[irow][icol] = 1 # wall
            elif layout[irow][icol] == '&': layout[irow][icol] = 2 # player
            elif layout[irow][icol] == 'B': layout[irow][icol] = 3 # box
            elif layout[irow][icol] == '.': layout[irow][icol] = 4 # goal
            elif layout[irow][icol] == 'X': layout[irow][icol] = 5 # box on goal
        colsNum = len(layout[irow])
        if colsNum < maxColsNum:
            layout[irow].extend([1 for _ in range(maxColsNum-colsNum)]) 

    #print(layout)
    return np.array(layout)
def transferToGameState2(layout, player_pos):
    """Transfer the layout of initial puzzle"""
    maxColsNum = max([len(x) for x in layout])
    temp = np.ones((len(layout), maxColsNum))
    for i, row in enumerate(layout):
        for j, val in enumerate(row):
            temp[i][j] = layout[i][j]

    temp[player_pos[1]][player_pos[0]] = 2
    return temp

def PosOfPlayer(gameState):
    """Return the position of agent"""
    return tuple(np.argwhere(gameState == 2)[0]) # e.g. (2, 2)

def PosOfBoxes(gameState):
    """Return the positions of boxes"""
    return tuple(tuple(x) for x in np.argwhere((gameState == 3) | (gameState == 5))) # e.g. ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5))

def PosOfWalls(gameState):
    """Return the positions of walls"""
    return tuple(tuple(x) for x in np.argwhere(gameState == 1)) # e.g. like those above

def PosOfGoals(gameState):
    """Return the positions of goals"""
    return tuple(tuple(x) for x in np.argwhere((gameState == 4) | (gameState == 5))) # e.g. like those above

def isEndState(posBox):
    """Check if all boxes are on the goals (i.e. pass the game)"""
    return sorted(posBox) == sorted(posGoals)

def isLegalAction(action, posPlayer, posBox):
    """Check if the given action is legal"""
    xPlayer, yPlayer = posPlayer
    if action[-1].isupper(): # the move was a push
        x1, y1 = xPlayer + 2 * action[0], yPlayer + 2 * action[1]
    else:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
    return (x1, y1) not in posBox + posWalls

def legalActions(posPlayer, posBox):
    """Return all legal actions for the agent in the current game state"""
    allActions = [[-1,0,'u','U'],[1,0,'d','D'],[0,-1,'l','L'],[0,1,'r','R']]
    xPlayer, yPlayer = posPlayer
    legalActions = []
    for action in allActions:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
        if (x1, y1) in posBox: # the move was a push
            action.pop(2) # drop the little letter
        else:
            action.pop(3) # drop the upper letter
        if isLegalAction(action, posPlayer, posBox):
            legalActions.append(action)
        else: 
            continue     
    return tuple(tuple(x) for x in legalActions) # e.g. ((0, -1, 'l'), (0, 1, 'R'))

def updateState(posPlayer, posBox, action):
    """Return updated game state after an action is taken"""
    xPlayer, yPlayer = posPlayer # the previous position of player
    newPosPlayer = [xPlayer + action[0], yPlayer + action[1]] # the current position of player
    posBox = [list(x) for x in posBox]
    if action[-1].isupper(): # if pushing, update the position of box
        posBox.remove(newPosPlayer)
        posBox.append([xPlayer + 2 * action[0], yPlayer + 2 * action[1]])
    posBox = tuple(tuple(x) for x in posBox)
    newPosPlayer = tuple(newPosPlayer)
    return newPosPlayer, posBox

def isFailed(posBox):
    """This function used to observe if the state is potentially failed, then prune the search"""
    rotatePattern = [[0,1,2,3,4,5,6,7,8],
                    [2,5,8,1,4,7,0,3,6],
                    [0,1,2,3,4,5,6,7,8][::-1],
                    [2,5,8,1,4,7,0,3,6][::-1]]
    flipPattern = [[2,1,0,5,4,3,8,7,6],
                    [0,3,6,1,4,7,2,5,8],
                    [2,1,0,5,4,3,8,7,6][::-1],
                    [0,3,6,1,4,7,2,5,8][::-1]]
    allPattern = rotatePattern + flipPattern

    for box in posBox:
        if box not in posGoals:
            board = [(box[0] - 1, box[1] - 1), (box[0] - 1, box[1]), (box[0] - 1, box[1] + 1), 
                    (box[0], box[1] - 1), (box[0], box[1]), (box[0], box[1] + 1), 
                    (box[0] + 1, box[1] - 1), (box[0] + 1, box[1]), (box[0] + 1, box[1] + 1)]
            for pattern in allPattern:
                newBoard = [board[i] for i in pattern]
                if newBoard[1] in posWalls and newBoard[5] in posWalls: return True
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posWalls: return True
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posBox: return True
                elif newBoard[1] in posBox and newBoard[2] in posBox and newBoard[5] in posBox: return True
                elif newBoard[1] in posBox and newBoard[6] in posBox and newBoard[2] in posWalls and newBoard[3] in posWalls and newBoard[8] in posWalls: return True
    return False

"""Implement all approcahes"""

def depthFirstSearch(gameState):
    time_start = time.time()
    """Implement depthFirstSearch approach"""
    beginBox = PosOfBoxes(gameState)
    beginPlayer = PosOfPlayer(gameState)

    startState = (beginPlayer, beginBox)
    frontier = collections.deque([[startState]])
    exploredSet = set()
    actions = [[0]] 
    temp = []
    while frontier:
        if time.time() - time_start < 990 :
            node = frontier.pop()
            node_action = actions.pop()
            if isEndState(node[-1][-1]):
                temp += node_action[1:]
                break
            if node[-1] not in exploredSet:
                exploredSet.add(node[-1])
                for action in legalActions(node[-1][0], node[-1][1]):
                    newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action)
                    if isFailed(newPosBox):
                        continue
                    frontier.append(node + [(newPosPlayer, newPosBox)])
                    actions.append(node_action + [action[-1]])
        else:
            break
    runtime = time.time()-time_start
    return (temp,runtime)

def breadthFirstSearch(gameState):
    time_start = time.time() # th???i gian kh???i ?????u tr?? ch??i
    """Implement breadthFirstSearch approach"""
    beginBox = PosOfBoxes(gameState) # tr???ng th??i c??c v???t ch?????ng ban ?????u
    beginPlayer = PosOfPlayer(gameState) # tr???ng th??i v??? tr?? kh???i ?????u nh??n v???t

    startState = (beginPlayer, beginBox) # e.g. ((2, 2), ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5))), kh???i t???o tr???ng th??i kh???i ?????u
    frontier = collections.deque([[startState]]) # kh???i t???o h??ng ?????i v???i tr???ng th??i kh???i ?????u
    actions = collections.deque([[0]]) # kh???i t???o m???ng h??nh ?????ng v???i kh???i ?????u l?? 0
    exploredSet = set() # Kh???i t???o t???p x??t ch???a c??c node ???? x??t
    temp = []
    ### Implement breadthFirstSearch here
    while frontier: # trong h??ng ?????i kh??c r???ng
        if time.time() - time_start < 990 :  # N???u th???i gian th???c hi???n nh??? h??n 990
            node = frontier.popleft() # l???y ra ph???n t??? ?????u b??n tr??i h??ng ?????i
            node_action = actions.popleft()  # l???y ph???n t??? ?????u b??n tr??i trong m???ng h??nh ?????ng
            if isEndState(node[-1][-1]): # N???u tr???ng th??i c??c v???t ch?????ng tr??ng v??? tr?? ????ch
                temp += node_action[1:] # ta l??u l???i chu???i h??nh ?????ng
                break # tho??t ra
            if node[-1] not in exploredSet: # N???u node ch??a c?? ch??a c?? trong x??t
                exploredSet.add(node[-1]) # th??m n?? v??o
                for action in legalActions(node[-1][0], node[-1][1]): # V???i t???t c??? h??nh ?????ng h???p l?? c???a t??c t??? t???i v??? tr?? hi???n t???i
                    newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][-1], action) # c???p nh???t tr???i th??i m???i
                    if isFailed(newPosBox): # N???u v??? tr?? v???t ch?????ng m???i g??y fail 
                        continue # th?? b??? qua h??nh ?????ng c???p nh???t tr???ng th??i v???a r???i
                    frontier.append(node + [(newPosPlayer, newPosBox)]) # Th??m v??o h??ng ?????i node cha v?? node tr???ng th??i con
                    actions.append(node_action + [action[-1]]) # Th??m v??o m???ng h?? h??nh ?????ng hi???n t???i v?? h??nh ?????ng d???n t???i node con
        else:
            break
    runtime = time.time()-time_start
    return (temp,runtime)

def cost(actions):
    """A cost function"""
    #print(actions)
    return len([x for x in actions if str(x).islower])

def uniformCostSearch(gameState):
    time_start = time.time() # th???i gian kh???i ?????u tr?? ch??i
    """Implement uniformCostSearch approach"""
    beginBox = PosOfBoxes(gameState)  # tr???ng th??i c??c v???t ch?????ng ban ?????u
    beginPlayer = PosOfPlayer(gameState) # tr???ng th??i v??? tr?? kh???i ?????u nh??n v???t

    startState = (beginPlayer, beginBox) # kh???i t???o tr???ng th??i kh???i ?????u
    frontier = PriorityQueue()  # kh???i t???o h??ng ?????i v???i tr???ng th??i kh???i ?????u
    frontier.push([startState], 0)  # Th??m v??o h??ng ?????i tr???ng th??i ban ?????u
    exploredSet = set() # Kh???i t???o t???p x??t ch???a c??c node ???? x??t
    actions = PriorityQueue()  # kh???i t???o m???ng h??nh ?????ng v???i kh???i ?????u
    actions.push([0], 0) # Th??m v??o h??nh ?????ng kh???i ?????u l?? 0
    temp = [] # m???ng k???t qu??? chu???i h??nh ?????ng
    ### Implement uniform cost search here
    while frontier:  # trong h??ng ?????i kh??c r???ng
        if time.time() - time_start < 990 :  # N???u th???i gian th???c hi???n nh??? h??n 990
            node = frontier.pop() #l???y ra ph???n t??? t??? cu???i h??ng ?????i
            node_action = actions.pop() # l???y ph???n t??? cu???i c??ng trong m???ng h??nh ?????ng
            #print(node_action)
            if node == -1: # N???u node r???ng
                break # tho??t
            if isEndState(node[-1][-1]): # N???u tr???ng th??i c??c v???t ch?????ng tr??ng v??? tr?? ????ch
                temp += node_action[1:] # ta l??u l???i chu???i h??nh ?????ng
                break  # tho??t ra
            if node[-1] not in exploredSet : # N???u node ch??a c?? ch??a c?? trong x??t
                exploredSet.add(node[-1])  # th??m n?? v??o (????nh d???u ???? x??t r???i)
                print(node_action[1:])
                Cost = cost(node_action[1:]) # t??nh l???i chi ph?? cho chu???i h??nh ?????ng t??? ?????u ?????n node hi???n t???i (b??? qua chi ph?? ?????y th??ng)
                for action in legalActions(node[-1][0], node[-1][1]): # v???i m???i h??nh ?????ng c?? th??? th???c hi???n ??? node ??ang x??t
                    newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action) # c???p nh???t tr???ng th??i m???i t??? h??nh ?????ng ????
                    if isFailed(newPosBox): # N???u tr???ng th??i v???t ch?????ng m???i g??y fail
                        continue # b??? qua tr???ng tr??i m???i v???a ???????c t???o ra
                    frontier.push(node + [(newPosPlayer, newPosBox)], Cost)  # Th??m v??o h??ng ?????i node cha v?? node tr???ng th??i con v???i ????? ??u ti??n theo cost
                    actions.push(node_action + [action[-1]], Cost) # Th??m v??o m???ng h?? h??nh ?????ng hi???n t???i v?? h??nh ?????ng d???n t???i node con v???i ????? ??u ti??n theo cost
        else:
            break
    runtime = time.time()-time_start
    return (temp,runtime)

"""Read command"""
def readCommand(argv):
    from optparse import OptionParser
    
    parser = OptionParser()
    parser.add_option('-l', '--level', dest='sokobanLevels',
                      help='level of game to play', default='level1.txt')
    parser.add_option('-m', '--method', dest='agentMethod',
                      help='research method', default='bfs')
    args = dict()
    options, _ = parser.parse_args(argv)
    with open('assets/levels/' + options.sokobanLevels,"r") as f: 
        layout = f.readlines()
    args['layout'] = layout
    args['method'] = options.agentMethod
    return args

def get_move(layout, player_pos, method):
    global posWalls, posGoals
    # layout, method = readCommand(sys.argv[1:]).values()
    gameState = transferToGameState2(layout, player_pos)
    posWalls = PosOfWalls(gameState)
    posGoals = PosOfGoals(gameState)

    if method == 'dfs':
        result, runtime = depthFirstSearch(gameState)
    elif method == 'bfs':
        result, runtime = breadthFirstSearch(gameState)    
    elif method == 'ucs':
        result, runtime= uniformCostSearch(gameState)
    else:
        raise ValueError('Invalid method.')
    print('Runtime of %s: %.2f second.' %(method, runtime))
    return (result,runtime)
    
