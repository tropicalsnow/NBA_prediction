import heapq

class MaxHeapObj(object):
    def __init__(self,val): self.val = val
    def __lt__(self,other): return self.val > other.val
    def __eq__(self,other): return self.val == other.val
    def __str__(self): return str(self.val) 

class MinHeap(object):
    def __init__(self): self.h = []
    def heappush(self,x): heapq.heappush(self.h,x)
    def heappop(self): return heapq.heappop(self.h)
    def __getitem__(self,i): return self.h[i]
    def __len__(self): return len(self.h)

class MaxHeap(MinHeap):
    def heappush(self,x): heapq.heappush(self.h,MaxHeapObj(x))
    def heappop(self): return heapq.heappop(self.h).val
    def __getitem__(self,i): return self.h[i].val



# Function implementing algorithm to find median so far. 
def getMedian(e, m, l, r):
        



    """ Signum function 
    = 0  if a == b  - heaps are balanced 
    = -1 if a < b   - left contains less elements than right 
    = 1  if a > b   - left contains more elements than right  """
    def Signum(a, b):

        if a == b : 
            return 0 

        if a<b:
            return -1
        else:
            return 1    
        
    
    def Average( a, b):
        return (a + b) / 2





    #Are heaps balanced? If yes, sig will be 0 
    sig = Signum(len(l), len(r))

    if sig==1: # There are more elements in left (max) heap 
        if  e < m: # current element fits in left (max) heap 
            
            #Remove top element from left heap and 
            #insert into right heap 
            r.heappush(l.heappop())

            # current element fits in left (max) heap 
            l.heappush(e)
        
        else:
            
            #current element fits in right (min) heap 
            r.heappush(e)
        
        #Both heaps are balanced 
        m = Average(l[0], r[0])

    
    elif sig == 0: #The left and right heaps contain same number of elements    
        
        if  e < m: #current element fits in left (max) heap 
            
            l.heappush(e) 
            m = l[0]

        else:

            # current element fits in right (min) heap 
            r.heappush(e) 
            m = r[0]


    else:  # There are more elements in right (min) heap 
        
        if  e < m: #current element fits in left (max) heap 
           
            l.heappush(e)
        
        else:

            # Remove top element from right heap and 
            # insert into left heap 
            l.heappush(r.heappop())

            # current element fits in right (min) heap 
            r.heappush(e) 

        # Both heaps are balanced 
        m = Average(l[0], r[0])

    # No need to return, m already updated 
    return m





#HOW TO USE EXAMPLE:

# m = 0 # effective median 
# A = [0.5377,    1.8339,   -2.2588,    0.8622,    0.3188,   -1.3077,   -0.4336,    0.3426,    3.5784,    2.7694]
# left =  MaxHeap()
# right = MinHeap()

# for i in range(len(A)):
#     m = getMedian(A[i], m, left, right)
  
#     print(m)

