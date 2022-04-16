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
    time_start = time.time() # thời gian khởi đầu trò chơi
    """Implement breadthFirstSearch approach"""
    beginBox = PosOfBoxes(gameState) # trạng thái các vật chướng ban đầu
    beginPlayer = PosOfPlayer(gameState) # trạng thái vị trí khởi đầu nhân vật

    startState = (beginPlayer, beginBox) # e.g. ((2, 2), ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5))), khởi tạo trạng thái khởi đầu
    frontier = collections.deque([[startState]]) # khởi tạo hàng đợi với trạng thái khởi đầu
    actions = collections.deque([[0]]) # khởi tạo mảng hành động với khởi đầu là 0
    exploredSet = set() # Khởi tạo tập xét chứa các node đã xét
    temp = []
    ### Implement breadthFirstSearch here
    while frontier: # trong hàng đợi khác rỗng
        if time.time() - time_start < 990 :  # Nếu thời gian thực hiện nhỏ hơn 990
            node = frontier.popleft() # lấy ra phần tử đầu bên trái hàng đợi
            node_action = actions.popleft()  # lấy phần tử đầu bên trái trong mảng hành động
            if isEndState(node[-1][-1]): # Nếu trạng thái các vật chướng trùng vị trí đích
                temp += node_action[1:] # ta lưu lại chuỗi hành động
                break # thoát ra
            if node[-1] not in exploredSet: # Nếu node chưa có chưa có trong xét
                exploredSet.add(node[-1]) # thêm nó vào
                for action in legalActions(node[-1][0], node[-1][1]): # Với tất cả hành động hợp lí của tác tử tại vị trí hiện tại
                    newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][-1], action) # cập nhật trại thái mới
                    if isFailed(newPosBox): # Nếu vị trí vật chướng mới gây fail 
                        continue # thì bỏ qua hành động cập nhật trạng thái vừa rồi
                    frontier.append(node + [(newPosPlayer, newPosBox)]) # Thêm vào hàng đợi node cha và node trạng thái con
                    actions.append(node_action + [action[-1]]) # Thêm vào mảng hđ hành động hiện tại và hành động dẫn tới node con
        else:
            break
    runtime = time.time()-time_start
    return (temp,runtime)

def cost(actions):
    """A cost function"""
    #print(actions)
    return len([x for x in actions if str(x).islower])

def uniformCostSearch(gameState):
    time_start = time.time() # thời gian khởi đầu trò chơi
    """Implement uniformCostSearch approach"""
    beginBox = PosOfBoxes(gameState)  # trạng thái các vật chướng ban đầu
    beginPlayer = PosOfPlayer(gameState) # trạng thái vị trí khởi đầu nhân vật

    startState = (beginPlayer, beginBox) # khởi tạo trạng thái khởi đầu
    frontier = PriorityQueue()  # khởi tạo hàng đợi với trạng thái khởi đầu
    frontier.push([startState], 0)  # Thêm vào hàng đợi trạng thái ban đầu
    exploredSet = set() # Khởi tạo tập xét chứa các node đã xét
    actions = PriorityQueue()  # khởi tạo mảng hành động với khởi đầu
    actions.push([0], 0) # Thêm vào hành động khởi đầu là 0
    temp = [] # mảng kết quả chuỗi hành động
    ### Implement uniform cost search here
    while frontier:  # trong hàng đợi khác rỗng
        if time.time() - time_start < 990 :  # Nếu thời gian thực hiện nhỏ hơn 990
            node = frontier.pop() #lấy ra phần tử từ cuối hàng đợi
            node_action = actions.pop() # lấy phần tử cuối cùng trong mảng hành động
            #print(node_action)
            if node == -1: # Nếu node rỗng
                break # thoát
            if isEndState(node[-1][-1]): # Nếu trạng thái các vật chướng trùng vị trí đích
                temp += node_action[1:] # ta lưu lại chuỗi hành động
                break  # thoát ra
            if node[-1] not in exploredSet : # Nếu node chưa có chưa có trong xét
                exploredSet.add(node[-1])  # thêm nó vào (đánh dấu đã xét rồi)
                print(node_action[1:])
                Cost = cost(node_action[1:]) # tính lại chi phí cho chuỗi hành động từ đầu đến node hiện tại (bỏ qua chi phí đẩy thùng)
                for action in legalActions(node[-1][0], node[-1][1]): # với mỗi hành động có thể thực hiện ở node đang xét
                    newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action) # cập nhật trạng thái mới từ hành động đó
                    if isFailed(newPosBox): # Nếu trạng thái vật chướng mới gây fail
                        continue # bỏ qua trạng trái mới vừa được tạo ra
                    frontier.push(node + [(newPosPlayer, newPosBox)], Cost)  # Thêm vào hàng đợi node cha và node trạng thái con với độ ưu tiên theo cost
                    actions.push(node_action + [action[-1]], Cost) # Thêm vào mảng hđ hành động hiện tại và hành động dẫn tới node con với độ ưu tiên theo cost
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
    
