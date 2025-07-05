import pandas as pd
from io import BytesIO
import xlsxwriter

def create_excel_file(income_data, expense_data):
    """Create an Excel file with income and expense data in separate sheets"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write income data
        if not income_data.empty:
            income_data.to_excel(writer, sheet_name='Income', index=False)
        else:
            pd.DataFrame(columns=['Sr', 'Date', 'Name', 'Amount']).to_excel(writer, sheet_name='Income', index=False)
        
        # Write expense data
        if not expense_data.empty:
            expense_data.to_excel(writer, sheet_name='Expenses', index=False)
        else:
            pd.DataFrame(columns=['Sr', 'Date', 'Name', 'Amount']).to_excel(writer, sheet_name='Expenses', index=False)
        
        # Create summary sheet
        total_income = income_data['Amount'].astype(float).sum() if not income_data.empty else 0
        total_expenses = expense_data['Amount'].astype(float).sum() if not expense_data.empty else 0
        net_balance = total_income - total_expenses
        
        summary_data = pd.DataFrame({
            'Metric': ['Total Income', 'Total Expenses', 'Net Balance'],
            'Amount': [total_income, total_expenses, net_balance]
        })
        summary_data.to_excel(writer, sheet_name='Summary', index=False)
        
        # Get workbook and add formatting
        workbook = writer.book
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        money_format = workbook.add_format({'num_format': 'Rs #,##0.00'})
        
        # Format income sheet
        if 'Income' in writer.sheets:
            worksheet = writer.sheets['Income']
            worksheet.set_column('A:A', 5)  # Sr column
            worksheet.set_column('B:B', 12)  # Date column
            worksheet.set_column('C:C', 25)  # Name column
            worksheet.set_column('D:D', 15, money_format)  # Amount column
            
            # Apply header format
            for col_num, value in enumerate(['Sr', 'Date', 'Name', 'Amount']):
                worksheet.write(0, col_num, value, header_format)
        
        # Format expense sheet
        if 'Expenses' in writer.sheets:
            worksheet = writer.sheets['Expenses']
            worksheet.set_column('A:A', 5)  # Sr column
            worksheet.set_column('B:B', 12)  # Date column
            worksheet.set_column('C:C', 25)  # Name column
            worksheet.set_column('D:D', 15, money_format)  # Amount column
            
            # Apply header format
            for col_num, value in enumerate(['Sr', 'Date', 'Name', 'Amount']):
                worksheet.write(0, col_num, value, header_format)
        
        # Format summary sheet
        if 'Summary' in writer.sheets:
            worksheet = writer.sheets['Summary']
            worksheet.set_column('A:A', 20)  # Metric column
            worksheet.set_column('B:B', 15, money_format)  # Amount column
            
            # Apply header format
            for col_num, value in enumerate(['Metric', 'Amount']):
                worksheet.write(0, col_num, value, header_format)
    
    output.seek(0)
    return output.getvalue()

def create_combined_csv(income_data, expense_data):
    """Create a combined CSV file with both income and expense data"""
    combined_data = []
    
    # Add income data
    if not income_data.empty:
        income_copy = income_data.copy()
        income_copy['Type'] = 'Income'
        combined_data.append(income_copy[['Sr', 'Date', 'Name', 'Amount', 'Type']])
    
    # Add expense data
    if not expense_data.empty:
        expense_copy = expense_data.copy()
        expense_copy['Type'] = 'Expense'
        combined_data.append(expense_copy[['Sr', 'Date', 'Name', 'Amount', 'Type']])
    
    if combined_data:
        combined_df = pd.concat(combined_data, ignore_index=True)
        return combined_df.to_csv(index=False)
    else:
        return pd.DataFrame(columns=['Sr', 'Date', 'Name', 'Amount', 'Type']).to_csv(index=False)

