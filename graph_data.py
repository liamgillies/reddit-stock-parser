import matplotlib.pyplot as plt

def plotTicker(name):
    f = open("reddit_data.txt", "r")
    line = f.readline()
    closing_prices = []
    positivity_ratings = []
    negativity_ratings = []
    counter_arr = []
    counter = 0
    while(line):
        if(len(line)<20):
            line = f.readline()
            continue
        line = line[1:-2].split(", ")
        line[0] = line[0][1:-1]
        if(line[0] != name):
            line = f.readline()
            continue
        line[1:4] = [float(line[i]) for i in range(1,4)]
        line[4] = int(line[4])
        counter_arr.append(counter)
        positivity_ratings.append(line[1])
        negativity_ratings.append(line[2])
        closing_prices.append(line[3])
        counter+=1
        line = f.readline()
    d1 = {'x': counter_arr, 'y': positivity_ratings}
    d2 = {'x1': counter_arr, 'y1': closing_prices}
    plt.plot('x', 'y', data=d1, marker='o', markerfacecolor='blue', markersize=12, color='skyblue', linewidth=4)
    plt.plot('x1', 'y1', data=d2, marker='o', markerfacecolor='blue', markersize=12, color='olive', linewidth=2)
    plt.show()

plotTicker('AAPL')