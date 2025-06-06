from django.urls import path
from .views import dashboard_data, dashboard_profit, summary_counts, top_parties_combined,get_total_profit,get_total_revenue, get_revenue_data, get_profit_data, get_yearly_earnings

urlpatterns = [
    path('dashboard/', dashboard_data, name='dashboard_data'),
    path('profit/', dashboard_profit, name='dashboard_profit'),
    path('total-revenue/', get_total_revenue, name='get_total_revenue_parties'),
    path('total-profit/', get_total_profit, name='get_total_profit'),
    path('summary-counts/', summary_counts, name='summary_counts'),
    path('top-parties-combined/', top_parties_combined, name='top_parties_combined'),
    path('revenue-data/', get_revenue_data, name='revenue-data'),
    path('profit-data/', get_profit_data, name='profit-data'),
    path('yearly-earnings/', get_yearly_earnings, name='yearly-earnings'),
]
