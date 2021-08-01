from smiteapi.smite import Smite, GODS_DICT, ITEMS_DICT
from analyzer import Analyzer

analyzer = Analyzer.from_db()

rs = analyzer.accumulated_result()

