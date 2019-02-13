
print 5//2

def horizontalGridLine(horizontalStart, horizontalEnd, horizontalGap, verticalStart, verticalSize, verticalInclination):
    numberOfSlots = (horizontalEnd - horizontalStart) // horizontalGap
    print horizontalStart
    print horizontalEnd
    print numberOfSlots
    trueEnd = horizontalStart + numberOfSlots * horizontalGap
    gridLine = []
    for i in range(0, numberOfSlots, 1):
        slot=[]
        x1 = horizontalStart+i*horizontalGap
        x2 = horizontalStart+(i+1)*horizontalGap
        y1 = verticalStart + i * verticalInclination
        y2 = y1+verticalSize
        slot.append(y1)
        slot.append(y2)
        slot.append(x1)
        slot.append(x2)
        gridLine.append(slot)
    return str(gridLine)
