from django.urls import path
from .views import gstr_1,receivable_ageing_report,party_ledger,party_wise_outstanding, party_report_by_item,stock_summary,stock_details_report,sales_summary,item_report_by_party,sales_summary_categorywise,rate_list,low_stock_summary,item_sales_and_purchase_summary,profit_and_loss,balance_sheet,gst_purchase_with_hsn, gst_sales_with_hsn,purchase_summary,hsn_wise_sales_summary,gstr_2_purchase,daybook,bill_wise_profit,cash_and_bank_report,tcs_payable,tcs_receivable,tds_payable,tds_receivable,expense_transaction_report, expense_category,audit_trial,gstr_3b
from . import views



urlpatterns = [
    path('party-wise-outstanding/', party_wise_outstanding, name='party_wise_outstanding'),
    path('party-report-by-item/', party_report_by_item, name='party_report_by_item'),
    path('stock-summary/', stock_summary, name='stock_summary'),
    path('stock-details-report/', stock_details_report, name='stock_details_report'),
    path('sales-summary/', sales_summary, name='sales_summary'),
    path('sales-summary-categorywise/', sales_summary_categorywise, name='sales_summary_categorywise'),
    path('item-report-by-party/', item_report_by_party, name='item_report_by_party'),
    path('receivable-ageing-report/', receivable_ageing_report, name='Receivable Ageing Report'),
    path('party-ledger/<int:party_id>/', party_ledger, name='party Ledger'),
    path('rate-list/', rate_list, name='rate_list'),
    path('low-stock-summary/', low_stock_summary, name='low_stock_summary'),
    path('item-sales-and-purchase_summary/', item_sales_and_purchase_summary, name='item_sales_and_purchase_summary'),
    path('profit-and-loss/', profit_and_loss, name='profit_and_loss'),
    path('gstr-1/', gstr_1, name='gstr-1'),
        
    path('current-liability-entries/', views.list_current_liability_entries, name='list_current_liability_entries'),
    path('current-liability-entries/add/', views.add_current_liability_entry, name='add_current_liability_entry'),
    path('current-liability-entries/<int:pk>/', views.current_liability_entry_detail, name='current_liability_entry_detail'),
    path('current-asset-entries/', views.list_current_asset_entries, name='list_current_asset_entries'),
    path('current-asset-entries/add/', views.add_current_asset_entry, name='add_current_asset_entry'),
    path('current-asset-entries/<int:pk>/', views.current_asset_entry_detail, name='current_asset_entry_detail'),
    path('loans-advance-entries/', views.list_loans_advance_entries, name='list_loans_advance_entries'),
    path('loans-advance-entries/add/', views.add_loans_advance_entry, name='add_loans_advance_entry'),
    path('loans-advance-entries/<int:pk>/', views.loans_advance_entry_detail, name='loans-advance-entry-detail'),
    path('investment-entries/', views.list_investment_entries, name='list_investment_entries'),
    path('investment-entries/add/', views.add_investment_entry, name='add_investment_entry'),
    path('investment-entries/<int:pk>/', views.investment_entry_detail, name='investment-entry-detail'),
    path('fixed-asset-entries/', views.list_fixed_asset_entries, name='list_fixed_asset_entries'),
    path('fixed-asset-entries/add/', views.add_fixed_asset_entry, name='add_fixed_asset_entry'),
    path('fixed-asset-entries/<int:pk>/', views.fixed_asset_entry_detail, name='fixed-asset-entry-detail'),
    path('loan-entries/', views.list_loan_entries, name='list_loan_entries'),
    path('loan-entries/add/', views.add_loan_entry, name='add_loan_entry'),
    path('loan-entries/<int:pk>/', views.loan_entry_detail, name='loan_entry_detail'),
    path('capital-entries/', views.list_capital_entries, name='list_capital_entries'),
    path('capital-entries/add/', views.add_capital_entry, name='add_capital_entry'),
    path('capital-entries/<int:pk>/', views.capital_entry_detail, name='capital-entry-detail'),
    path('balance-sheet/', balance_sheet, name='balance sheet'),
    
    path('gst-purchase-with-hsn/', gst_purchase_with_hsn, name='gst_purchase_with_hsn'),
    path('gst-sales-with-hsn/', gst_sales_with_hsn, name='gst_sales_with_hsn'),
    path('purchase-summary/', purchase_summary, name='purchase_summary'),
    path('hsn-wise-sales-summary/', hsn_wise_sales_summary, name='hsn_wise_sales_summary'),
    path('gstr-2-purchase/', gstr_2_purchase, name='gstr_2_purchase'),
    path('daybook/', daybook, name='daybook'),
    path('bill-wise-profit/', bill_wise_profit, name='bill_wise_profit'),
    path('cash-and-bank-report/', cash_and_bank_report, name='cash_and_bank_report'),
    path('tcs-payable/', tcs_payable, name='tcs_payable'),
    path('tcs-receivable/', tcs_receivable, name='tcs_receivable'),
    path('tds-payable/', tds_payable, name='tds_payable'),
    path('tds-receivable/', tds_receivable, name='tds_receivable'),
    path('expense-transaction-report/', expense_transaction_report, name='expense_transaction_report'),
    path('expense-category/',  expense_category, name=' expense_category'),
    path('audit-trial/', audit_trial, name='audit_trial'),
    path('gstr-3b/', gstr_3b, name='gstr-3b'),
   

]

