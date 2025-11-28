from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class CustomUser(AbstractUser):
    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.username

class deviceDetails(models.Model):
    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, db_column='user_id')
    device_name = models.CharField(max_length=15, db_column='device_name')
    device_id = models.CharField(max_length=255, db_column='device_id')
    registered_at = models.DateTimeField(auto_now_add=True, db_column='registered_at')
    last_login_at = models.DateTimeField(db_column='last_login_at')

    class Meta:
        db_table = 'device_details'
        unique_together = ('device_name', 'device_id')

    def __str__(self):
        return self.device_name

class MetaData(models.Model):
    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, db_column='user_id')
    dateTime = models.DateTimeField(auto_now_add=True, db_column='date_time')
    deviceName = models.CharField(max_length=255, null=True, db_column='device_name')

    class Meta:
        db_table = 'meta_data'

class Todo(models.Model):
    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, db_column='user_id')
    todoName = models.CharField(max_length=255, db_column='todo_name')
    todoDate = models.DateTimeField(db_column='todo_date')
    isCompleted = models.BooleanField(default=False, db_column='is_completed')
    isRegular = models.BooleanField(default=False, db_column='is_regular')
    insertAt = models.ForeignKey(MetaData, on_delete=models.SET_NULL, null=True, db_column = 'insert_at', related_name='todo_inserts')
    updateAt = models.ForeignKey(MetaData, on_delete=models.SET_NULL, null=True, db_column = 'update_at', related_name='todo_updates')

    class Meta:
        db_table = 'todo'

    def __str__(self):
        return self.todoName
    
class StockNames(models.Model):
    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    stockName = models.CharField(max_length=150, db_column='stock_name')
    stockCode = models.CharField(max_length=50, db_column='stock_code')
    yCode = models.CharField(max_length=50, db_column='yhoo_code')
    isActive = models.BooleanField(default=False, db_column='is_active')
    insertAt = models.ForeignKey(MetaData, on_delete=models.SET_NULL, null=True, db_column = 'insert_at', related_name='stock_inserts')
    updateAt = models.ForeignKey(MetaData, on_delete=models.SET_NULL, null=True, db_column = 'update_at', related_name='stock_updates')
    sector = models.CharField(max_length=150, null=True, db_column='sector')
    industry = models.CharField(max_length=150, null=True,  db_column='industry')
    isFno = models.BooleanField(default=False, db_column='is_fno')
    stockSlug = models.CharField(max_length=150, null=True, db_column='stock_slug')
    strongUpdatedOn = models.DateField(null=True, blank=True)
    sectorUpdatedOn = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'stock_names'

    def __str__(self):
        return self.stockName
    
class TradeData(models.Model):
    stock = models.ForeignKey(StockNames, on_delete=models.CASCADE, null=True, db_column = 'stock', related_name='stock_name')
    date = models.DateField(db_column='date')
    startDate = models.DateField(null=True,db_column='start_date')
    endDate = models.DateField(null=True,db_column='end_date')
    prevDate = models.DateField(null=True,db_column='prev_date')
    open = models.FloatField(db_column='open')
    close = models.FloatField(db_column='close')
    low = models.FloatField(db_column='low')
    high = models.FloatField(db_column='high')
    adjClose = models.FloatField(db_column='adjClose')
    volume = models.BigIntegerField(db_column='volume') 
    updatedAt = models.DateField(auto_now_add=True, db_column='updated_at')
    # ema5 = models.FloatField(null=True, db_column='ema5')
    # ema20 = models.FloatField(null=True, db_column='ema20')
    # sma50 = models.FloatField(null=True, db_column='sma50')
      
    
    class Meta:
        db_table = 'trade_data'

    def __int__(self):
        return self.id

class Holidays(models.Model):
    holiday = models.DateField()
    reason = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'holidays'
        
    def __int__(self):
        return self.id
    
class SwingData(models.Model):
    stock = models.ForeignKey(StockNames, on_delete=models.CASCADE, null=True, db_column = 'stock', related_name='swing_stock_name')
    date = models.DateField(db_column='date')
    startDate = models.DateField(null=True,db_column='start_date')
    endDate = models.DateField(null=True,db_column='end_date') 
    ema5 = models.FloatField(null=True, db_column='ema5')
    ema20 = models.FloatField(null=True, db_column='ema20')
    sma50 = models.FloatField(null=True, db_column='sma50')
    updatedAt = models.DateField(auto_now_add=True, db_column='updated_at')
    close = models.FloatField(null=True, db_column='close')
      
    
    class Meta:
        db_table = 'swing_data'

    def __int__(self):
        return self.id
    
class StockCodes(models.Model):
    stockCode = models.CharField(max_length=50, db_column='stock_code')
    isUsed = models.BooleanField(default=False, db_column='is_used')     
    lastFetchedOn = models.DateField(null=True, blank=True)

    
    class Meta:
        db_table = 'stock_codes'

    def __int__(self):
        return self.id
    
class StockRatios(models.Model):
    stock = models.ForeignKey(StockNames, on_delete=models.CASCADE, null=True, db_column = 'stock', related_name='ratio_stock_name')
    risk = models.FloatField(null=True, blank=True)
    m3AvgVol = models.FloatField(null=True, blank=True)
    wpct_4 = models.FloatField(null=True, blank=True) 
    w52High = models.FloatField(null=True, blank=True)
    w52Low = models.FloatField(null=True, blank=True)
    wpct_52 = models.FloatField(null=True, blank=True) 
    beta = models.FloatField(null=True, blank=True)
    bps = models.FloatField(null=True, blank=True)
    divYield = models.FloatField(null=True, blank=True)
    eps = models.FloatField(null=True, blank=True)
    inddy = models.FloatField(null=True, blank=True)
    indpb = models.FloatField(null=True, blank=True)
    indpe = models.FloatField(null=True, blank=True)
    marketCap = models.FloatField(null=True, blank=True)
    mrktCapRank = models.IntegerField(null=True, blank=True)
    pb = models.FloatField(null=True, blank=True)
    pe = models.FloatField(null=True, blank=True)
    roe = models.FloatField(null=True, blank=True)
    nShareholders = models.IntegerField(null=True, blank=True)
    lastPrice = models.FloatField(null=True, blank=True)
    ttmPe = models.FloatField(null=True, blank=True)
    marketCapLabel = models.CharField(max_length=50, null=True, blank=True)
    m12Vol = models.FloatField(null=True, blank=True) 
    mrktCapf = models.FloatField(null=True, blank=True)
    apef = models.FloatField(null=True, blank=True)
    pbr = models.FloatField(null=True, blank=True)
    etfLiq = models.FloatField(null=True, blank=True)
    etfLiqLabel = models.CharField(max_length=50, null=True, blank=True)
    dayChange = models.FloatField(null=True, blank=True)
    weekChange = models.FloatField(null=True, blank=True)
    monthChange = models.FloatField(null=True, blank=True)
    away52H = models.FloatField(null=True, blank=True)
    away52L = models.FloatField(null=True, blank=True)
    volumeBreakOut = models.FloatField(null=True, blank=True)
    isCrossedHigh = models.BooleanField(default=False, null=True)
    isCrossedLow = models.BooleanField(default=False, null=True)

    class Meta:
        db_table = 'stock_ratios'
    def __str__(self):
        return f"StockJson(id={self.id})"

class StockHoldings(models.Model):
    stock = models.ForeignKey(StockNames, on_delete=models.CASCADE, null=True, db_column = 'stock', related_name='holding_stock_name')
    date = models.DateField(null=True)
    pmPctT= models.FloatField(null=True, blank=True)
    pmPctP= models.FloatField(null=True, blank=True)
    plPctT= models.FloatField(null=True, blank=True)
    uPlPctT= models.FloatField(null=True, blank=True)
    mfPctT= models.FloatField(null=True, blank=True)
    isPctT= models.FloatField(null=True, blank=True)
    diPctT= models.FloatField(null=True, blank=True)
    othDiPctT= models.FloatField(null=True, blank=True)
    othExInsDiPctT= models.FloatField(null=True, blank=True)
    fiPctT=models.FloatField(null=True, blank=True)
    rhPctT= models.FloatField(null=True, blank=True)
    othPctT= models.FloatField(null=True, blank=True)
    rOthPctT= models.FloatField(null=True, blank=True)
    class Meta:
        db_table = 'stock_holdings'

    def __int__(self):
        return self.id

class StockProfitRatios(models.Model):
    stock = models.ForeignKey(StockNames, on_delete=models.CASCADE, null=True, db_column = 'stock', related_name='profit_stock_name')
    pat = models.FloatField(null=True, blank=True)
    ebita= models.FloatField(null=True, blank=True)
    ebitam= models.FloatField(null=True, blank=True)
    roe= models.FloatField(null=True, blank=True)
    roce= models.FloatField(null=True, blank=True)
    roa= models.FloatField(null=True, blank=True)
    eps= models.FloatField(null=True, blank=True)
    updatedOn = models.DateField(null=True, blank=True)

    class Meta:
        db_table ='stock_profit_ratios'

    def __int__(self):
        return self.id
    

class StockLeverageRatios(models.Model):
    stock = models.ForeignKey(StockNames, on_delete=models.CASCADE, null=True, db_column = 'stock', related_name='lvr_stock_name')
    intCover = models.FloatField(null=True, blank=True)
    debtEq=models.FloatField(null=True, blank=True)
    debtAs=models.FloatField(null=True, blank=True)
    finLe = models.FloatField(null=True, blank=True)

    class Meta:
        db_table ='stock_leverage_ratios'

    def __int__(self):
        return self.id
    
class StockValuationRatios(models.Model):
    stock = models.ForeignKey(StockNames, on_delete=models.CASCADE, null=True, db_column = 'stock', related_name='vlt_stock_name')
    pe = models.FloatField(null=True, blank=True)
    pbv= models.FloatField(null=True, blank=True)
    ps= models.FloatField(null=True, blank=True) 

    class Meta:
        db_table = 'stock_valuation_ratios'

    def __int__(self):
        return self.id
    
class StockOperatingRatios(models.Model):
    stock = models.ForeignKey(StockNames, on_delete=models.CASCADE, null=True, db_column = 'stock', related_name='oprt_stock_name')
    fxtr= models.FloatField(null=True, blank=True)
    wctr= models.FloatField(null=True, blank=True)
    tatr= models.FloatField(null=True, blank=True)
    rtr= models.FloatField(null=True, blank=True)

    class Meta:
        db_table ='stock_operating_ratios'

    def __int__(self):
        return self.id

class StockCommentary(models.Model):
    stock = models.ForeignKey(StockNames, on_delete=models.CASCADE, null=True, db_column = 'stock', related_name='cmnt_stock_name')
    item = models.CharField(max_length=100,null=True)
    itemType = models.CharField(max_length=100,null=True) 
    mood = models.CharField(max_length=100,null=True)
    title=models.CharField(max_length=100,null=True)
    message = models.TextField(null=True)
    description=models.TextField(null=True)
    tag   =models.CharField(max_length=100,null=True)

    class Meta:
        db_table='stock_commentary'

    def __int__(self):
        return self.id

class StockForecast(models.Model):
    stock = models.ForeignKey(StockNames, on_delete=models.CASCADE, null=True, db_column = 'stock', related_name='forecast_stock_name')
    total=models.FloatField(null=True)
    buy=models.FloatField(null=True)
    sell= models.FloatField(null=True)
    nuet=models.FloatField(null=True)

    class Meta:
        db_table='stock_forecast'

    def __int__(self):
        return self.id


class SwingStocks(models.Model):
    stock = models.ForeignKey(StockNames, on_delete=models.CASCADE, null=True, db_column = 'stock', related_name='sw_stock_name')
    com_rank=models.FloatField(null=True)
    div_rank=models.FloatField(null=True)
    hol_rank=models.FloatField(null=True)
    tot_rank=models.FloatField(null=True)
    date = models.DateField(null=True)
    fore_rank=models.FloatField(null=True)
    is_sector=models.BooleanField(default=False)

    class Meta:
        db_table='swing_stocks'

    def __int__(self):
        return self.id
    
class TrendySector(models.Model):
    sector = models.CharField(null=True, max_length=50)
    no=models.IntegerField(null=True)
    week=models.FloatField(null=True)
    month=models.FloatField(null=True)
    perc=models.FloatField(null=True)
    updatedOn=models.DateField(null=True, blank=True)

    class Meta:
        db_table='trendy_sector'

    def __int__(self):
        return self.id
    
class LongStocks(models.Model):
    stock = models.ForeignKey(StockNames, on_delete=models.CASCADE, null=True, db_column = 'stock', related_name='lg_stock_name')
    five_yr_avg_rtn_inst= models.FloatField(null=True)
    five_yr_hist_rvnu_grth= models.FloatField(null=True)
    one_yr_hist_rvnu_grth= models.FloatField(null=True)
    debt_eqty= models.FloatField(null=True)
    roce= models.FloatField(null=True)
    item=models.CharField(null=True, max_length=20)
    five_yr_roe= models.FloatField(null=True)
    away_from= models.FloatField(null=True)
    pe= models.FloatField(null=True)
    score = models.FloatField(default=0)
    recommendation = models.CharField(max_length=20, default="Hold")

    class Meta:
        db_table='long_stocks'

    def __int__(self):
        return self.id

class Goals(models.Model):
    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, db_column='user_id')
    goal_name = models.CharField(null=True, max_length=100)
    goal_amnt = models.FloatField(null=True)
    isAchieved  = models.BooleanField(default=False)
    insertAt = models.ForeignKey(MetaData, on_delete=models.SET_NULL, null=True, db_column = 'insert_at', related_name='goal_inserts')
    updateAt = models.ForeignKey(MetaData, on_delete=models.SET_NULL, null=True, db_column = 'update_at', related_name='goal_updates')

    class Meta:
        db_table ='goals'

    def __int__(self):
        return self.id

class assets(models.Model):
    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, db_column='user_id')
    asset_name = models.CharField(null=True, max_length=100)
    asset_amnt = models.FloatField(null=True)
    purchased_on = models.DateTimeField()
    valid_on = models.DateTimeField(null=True)
    insertAt = models.ForeignKey(MetaData, on_delete=models.SET_NULL, null=True, db_column = 'insert_at', related_name='asset_inserts')
    updateAt = models.ForeignKey(MetaData, on_delete=models.SET_NULL, null=True, db_column = 'update_at', related_name='asset_updates')

    class Meta:
        db_table='assets'

    def __int__(self):
        return self.id

class mfNames(models.Model):
    mfName=models.CharField(max_length=100)
    isActive=models.BooleanField(default=True)

    class Meta:
        db_table='mf_names'
    
    def __str__(self):
        return self.mfName

class MultibaggerScore(models.Model):
    stock = models.OneToOneField(StockNames, on_delete=models.CASCADE, related_name="mb_score")

    score = models.FloatField(default=0)          # Final Score 0–100
    fundamentals = models.FloatField(default=0)   # 0–100
    technicals = models.FloatField(default=0)     # 0–100
    momentum = models.FloatField(default=0)       # 0–100
    promoter = models.FloatField(default=0)       # 0–100
    sector = models.FloatField(default=0)         # 0–100

    updatedOn = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.stock.stockName} → {self.score}"
