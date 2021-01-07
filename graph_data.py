import matplotlib.pyplot as plt

def plotTicker(names):
    for name in names:
        fig, ax = plt.subplots(nrows=2, constrained_layout=True)
        fig.suptitle(name)
        f = open("reddit_data.txt", "r")
        line = f.readline()
        closing_prices = []
        positivity_ratings = []
        negativity_ratings = []
        counter_arr = []
        counter = 0
        while(line):
            if(line[0]!='['):
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
        d1 = {'counter': counter_arr, 'closing': closing_prices}
        d2 = {'counter': counter_arr, 'positivity': positivity_ratings}
        ax[0].title.set_text("Stock price")
        ax[0].plot('counter', 'closing', data=d1, marker='o', markerfacecolor='blue', markersize=12, color='skyblue', linewidth=4)
        ax[1].title.set_text("Positivity Rating")
        ax[1].plot('counter', 'positivity', data=d2, marker='o', markerfacecolor='blue', markersize=12, color='olive', linewidth=2)
        plt.show()

plotTicker(['TSLA', 'AAPL', 'NIO', 'AMD', 'BABA', 'AMZN', 'RIOT'])