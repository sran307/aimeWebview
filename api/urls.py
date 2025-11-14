
from django.urls import path
# from .views import Usercreate
# from .views import AuthView
from .views import views, stock_views, stock_ai, trade_analysis,goal, asset
urlpatterns = [
    # path('login/', views.as_view),
    path('checkExist/', views.checkDeviceExist),
    path('register/', views.registerUser),
    path('login/', views.loginUser),
    path('todo/ins/', views.todoInsert),
    path('todo/list/', views.todoList),
    path('todo/update/', views.todoUpdate),
    
    path('stock/codes/', stock_views.getStockCode, name='get_stock_code'),
    path('stock/names/', stock_views.getStockName, name='get_stock_name'),
    path('stock/quotes/', stock_views.getQuotes, name='get_strong_stocks'),
    path('stock/daily/', stock_views.getDailyData, name='get_daily_data'),
    path('stock/screen/', stock_views.dataScreen, name="data_screen_stocks"),
    path('stock/holidays/', stock_views.getHolidays, name='get_holidays'),
    # path('stock/predict/', stock_ai.getPredictPrice),
    
    path('stock/fundas/', stock_views.GetFundas, name="get_fundamentals"),
    path('stock/slug/', stock_views.GetSlug, name="get_slug"),
    path('stock/penny/', stock_views.GetPenny, name='get_penny_stocks'),
    path('stock/sector/', stock_views.getSector, name="get_sector"),

    path('trendy/sector/', trade_analysis.getTrendySector, name="get_trending_sector"),
    path('swing/analys/', trade_analysis.swingAnalysis, name="get_swing_stocks"),
    path('stock/long/', trade_analysis.getLong, name="get_long_stocks"),

    path('stock/52low/', trade_analysis.get52Low, name="get_52_low"),
    path('stock/52high/', trade_analysis.get52High, name="get_52_high"),

    path('goal/save/', goal.save),
    path('goal/list/', goal.list),

    path('asset/save/', asset.save),
    path('asset/list/', asset.list),
    path('asset/amnt/', asset.amnt),
    path('asset/update/', asset.update),




]
