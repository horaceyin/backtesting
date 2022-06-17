import sma_crossover
import yfinance
from pyalgotrade import plotter
#from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.barfeed import csvfeed
from pyalgotrade.bar import Frequency
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.stratanalyzer import trades

import pandas as pd
import requests
import json
from datetime import datetime
import time

URL = 'https://chart3.spsystem.info/pserver/chartdata_query.php?days=1&second=5&prod_code=HSIM2'

def print_result(strat, retAnalyzer, sharpeRatioAnalyzer, drawDownAnalyzer, tradesAnalyzer):
    print("")
    print("Final portfolio value: $%.2f" % strat.getResult())
    print("Cumulative returns: %.2f %%" % (retAnalyzer.getCumulativeReturns()[-1] * 100))
    print("Sharpe ratio: %.2f" % (sharpeRatioAnalyzer.getSharpeRatio(0.05)))
    print("Max. drawdown: %.2f %%" % (drawDownAnalyzer.getMaxDrawDown() * 100))
    print("Longest drawdown duration: %s" % (drawDownAnalyzer.getLongestDrawDownDuration()))

    print("")
    print("Total trades: %d" % (tradesAnalyzer.getCount()))
    if tradesAnalyzer.getCount() > 0:
        profits = tradesAnalyzer.getAll()
        print("Avg. profit: $%2.f" % (profits.mean()))
        print("Profits std. dev.: $%2.f" % (profits.std()))
        print("Max. profit: $%2.f" % (profits.max()))
        print("Min. profit: $%2.f" % (profits.min()))
        returns = tradesAnalyzer.getAllReturns()
        print(profits.tolist())
        # print(returns.tolist())
        # sum = 0.0
        # for x in returns.tolist():
        #     sum += x
        # print(sum / len(returns.tolist()) * 100, "!!!!!!!!!!!!")
        print(max(returns.tolist()))
        print(min(returns.tolist()))
        print("Avg. return: %2.2f %%" % (returns.mean() * 100))
        print("Returns std. dev.: %2.2f %%" % (returns.std() * 100))
        print("Max. return: %2.2f %%" % (returns.max() * 100))
        print("Min. return: %2.2f %%" % (returns.min() * 100))

    print("")
    print("Profitable trades: %d" % (tradesAnalyzer.getProfitableCount()))
    if tradesAnalyzer.getProfitableCount() > 0:
        profits = tradesAnalyzer.getProfits()
        print("Avg. profit: $%2.2f" % (profits.mean()))
        print("Profits std. dev.: $%2.2f" % (profits.std()))
        print("Max. profit: $%2.2f" % (profits.max()))
        print("Min. profit: $%2.2f" % (profits.min()))
        returns = tradesAnalyzer.getPositiveReturns()
        print("Avg. return: %2.2f %%" % (returns.mean() * 100))
        print("Returns std. dev.: %2.2f %%" % (returns.std() * 100))
        print("Max. return: %2.2f %%" % (returns.max() * 100))
        print("Min. return: %2.2f %%" % (returns.min() * 100))

    print("")
    print("Unprofitable trades: %d" % (tradesAnalyzer.getUnprofitableCount()))
    if tradesAnalyzer.getUnprofitableCount() > 0:
        losses = tradesAnalyzer.getLosses()
        print("Avg. loss: $%2.2f" % (losses.mean()))
        print("Losses std. dev.: $%2.2f" % (losses.std()))
        print("Max. loss: $%2.2f" % (losses.min()))
        print("Min. loss: $%2.2f" % (losses.max()))
        returns = tradesAnalyzer.getNegativeReturns()
        print("Avg. return: %2.2f %%" % (returns.mean() * 100))
        print("Returns std. dev.: %2.2f %%" % (returns.std() * 100))
        print("Max. return: %2.2f %%" % (returns.max() * 100))
        print("Min. return: %2.2f %%" % (returns.min() * 100))


def constructData(dataList):
    dateCol = []
    openCol = []
    highCol = []
    lowCol = []
    closeCol = []
    volumeCol = []
    for bar in dataList:
        dateCol.append(bar[0])
        openCol.append(bar[1])
        highCol.append(bar[2])
        lowCol.append(bar[3])
        closeCol.append(bar[4])
        volumeCol.append(bar[5])
    return (dateCol, openCol, highCol, lowCol, closeCol, volumeCol)

def main(plot, smaPeriod):
    instrument = "HSIM2"
    mySmaPeriod = smaPeriod
    date_time = datetime.fromtimestamp(int(time.time()))
    todayStrDate = date_time.strftime('%Y%m%d')
    csvName = 'HSIM2-' + todayStrDate + '-sp.csv'

    # Download the bars.
    myFeed = csvfeed.GenericBarFeed(Frequency.SECOND * 5)
    #feed = yahoofeed.Feed()
    #data = yfinance.download(instrument, start='2007-1-1', end = '2013-6-9')
    res = requests.get(url = URL)
    if res.status_code < 400:
        ownData = res.text
        tempData1 = ownData.split(':')
        tempData2 = tempData1[4].split(',0\r\n')
        mapData = map(lambda bar: bar.split(','), tempData2)
        newData = list(mapData)
        newData.pop()
        for i, bar in enumerate(newData):
            oriDate = bar.pop()
            dateTime = datetime.fromtimestamp(int(oriDate))
            strDate = dateTime.strftime('%Y-%m-%d %H:%M:%S')
            #print(strDate)
            bar.insert(0, strDate)
    dateCol, openCol, highCol, lowCol, closeCol, volumeCol = constructData(newData)
    pdData = {
        'Date Time': dateCol,
        'Open': openCol,
        'High': highCol,
        'Low': lowCol,
        'Close': closeCol,
        #'Adj Close': closeCol,
        'Volume': volumeCol
    }
    df = pd.DataFrame(pdData).set_index('Date Time')
    df.to_csv(csvName)
    print(len(dateCol))

    myFeed.addBarsFromCSV(instrument, csvName)
    strat = sma_crossover.SMACrossOver(myFeed, instrument, mySmaPeriod)

    retAnalyzer = returns.Returns()
    strat.attachAnalyzer(retAnalyzer)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    strat.attachAnalyzer(sharpeRatioAnalyzer)
    drawDownAnalyzer = drawdown.DrawDown()
    strat.attachAnalyzer(drawDownAnalyzer)
    tradesAnalyzer = trades.Trades()
    strat.attachAnalyzer(tradesAnalyzer)

    if plot:
        plt = plotter.StrategyPlotter(strat, True, False, True)
        plt.getInstrumentSubplot(instrument).addDataSeries("sma", strat.getSMA())

    strat.run()
    #print("Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(0.05))
    print_result(strat, retAnalyzer, sharpeRatioAnalyzer, drawDownAnalyzer, tradesAnalyzer)

    if plot:
        plt.plot()

    #print(data)
    # print(type(data))
    # print(dir(data))
    # df = dfSetUp()
    # print(df)
    # df.to_csv("xx.csv")
    # dataa = data[['Open', 'High', 'Low', 'Close', 'Volume']]
    # print(dataa)
    # dataa.to_csv("AAPL.csv")
    # feed.addBarsFromCSV(instrument, "AAPL.csv")
    # strat = sma_crossover.SMACrossOver(feed, instrument, smaPeriod)
    # sharpeRatioAnalyzer = sharpe.SharpeRatio()
    # strat.attachAnalyzer(sharpeRatioAnalyzer)

    # if plot:
    #     plt = plotter.StrategyPlotter(strat, True, False, True)
    #     plt.getInstrumentSubplot(instrument).addDataSeries("sma", strat.getSMA())

    # strat.run()
    # print("Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(0.05))

    # if plot:
    #     plt.plot()


if __name__ == "__main__":
    main(True, 163)