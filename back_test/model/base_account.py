import pandas as pd
from back_test.model.abstract_account import AbstractAccount
from back_test.model.constant import Util, TradeType, LongShort
from back_test.model.trade import Order


class BaseAccount():
    def __init__(self, init_fund, leverage=1.0, fee_rate=3.0 / 10000.0, rf=0.03):
        # super().__init__()
        self.df_records = pd.DataFrame()
        self.list_records = []
        self.trade_book = pd.DataFrame
        self.dict_holding = {} # id_instrument -> Product
        self.account = pd.DataFrame()
        self.init_fund = init_fund
        self.leverage = leverage
        self.fee_rate = fee_rate
        self.rf = rf
        self.cash = init_fund  # 现金账户：初始资金为现金
        self.total_portfolio_value = init_fund  # 投资组合总市值：初始状态只有现金
        self.total_invest_market_value = 0.0  # 投资市值，不包括现金

    # def add_record_1(self, dt_trade, id_instrument, trade_type, trade_price, trade_cost, trade_unit,
    #                  trade_margin_capital=0.0):
    #     record = pd.DataFrame(data={Util.ID_INSTRUMENT: [id_instrument],
    #                                 Util.DT_TRADE: [dt_trade],
    #                                 Util.TRADE_TYPE: [trade_type],
    #                                 Util.TRADE_PRICE: [trade_price],
    #                                 Util.TRANSACTION_COST: [trade_cost],
    #                                 Util.TRADE_UNIT: [trade_unit],  # 多空体现在unit正负号
    #                                 Util.TRADE_MARGIN_CAPITAL: [trade_margin_capital]
    #                                 })
    #     self.df_trading_records = self.df_trading_records.append(record, ignore_index=True)

    def add_record(self, execution_record: pd.Series):
        self.list_records.append(execution_record)
        # TODO : 及时计算账户资产、现金、保证金、杠杆等基本要素
        id_instrument = execution_record[Util.ID_INSTRUMENT]
        if id_instrument in self.trade_book[Util.ID_INSTRUMENT]:
            # close out:
            if self.trade_book.loc[id_instrument, Util.TRADE_UNIT] + execution_record[Util.TRADE_UNIT] == 0:
                self.dict_holding.pop(id_instrument,None)
                self.trade_book.loc[id_instrument, Util.TRADE_UNIT] = 0
                self.trade_book.loc[id_instrument, Util.TRADE_REALIZED_PNL] = \
                    execution_record[Util.TRADE_UNIT]* execution_record[Util.TRADE_PRICE] + \
                    self.trade_book.loc[id_instrument, Util.TRADE_UNIT]*self.trade_book.loc[id_instrument,Util.AVERAGE_HOLDING_COST]

            # add position
            total_unit = self.trade_book.loc[id_instrument, Util.TRADE_LONG_SHORT].value * \
                         self.trade_book.loc[id_instrument, Util.TRADE_UNIT] + \
                         execution_record[Util.TRADE_LONG_SHORT].value * execution_record[Util.TRADE_UNIT]
            total_position_size = execution_record[Util.TRADE_BOOK_VALUE] + self.trade_book.loc[id_instrument, Util.TRADE_BOOK_VALUE]
            realized_pnl =

            self.trade_book.loc[order.id_instrument, Util.TRADE_UNIT] = abs(total_unit)
            if total_unit > 0:
                self.trade_book.loc[order.id_instrument, Util.TRADE_LONG_SHORT] = LongShort.LONG
            else:
                self.trade_book.loc[order.id_instrument, Util.TRADE_LONG_SHORT] = LongShort.SHORT

    def get_investable_market_value(self):
        return self.cash * self.leverage

    def get_current_leverage(self):
        return self.total_portfolio_value / self.cash

    def daily_accounting(self):
        # TODO : recalculate margin requirements in a daily basis.

        return self.account

    def open_long(self, dt_trade, id_instrument, trade_price, trade_unit, name_code):
        trade_type = TradeType.OPEN_LONG
        trade_cost = trade_price * trade_unit * self.fee_rate
        # TODO: get trade margin capital by product code.
        trade_margin_capital = 0.0
        self.add_record(dt_trade, id_instrument, trade_type, trade_price, trade_cost, trade_unit, trade_margin_capital)
