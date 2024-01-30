# importing the required modules  
from tkinter import *                   
from tkinter import ttk as ttk          
from tkinter import messagebox as mb    
import datetime                         
import sqlite3                          
from tkcalendar import DateEntry        

# Tracker Utility Functions

def listAllExpenses():
    '''Retrieves data from the database and inserts it to the tkinter data table'''

    global dbconnector, data_table
    # Retrieve the data from the database
    all_data = dbconnector.execute('SELECT * FROM ExpenseTracker')  
    # Clear the data table
    data_table.delete(*data_table.get_children())    
    # List all data from the database on data table  
    data = all_data.fetchall()  
      
    # Insert values in data table  
    for val in data:  
        data_table.insert('', END, values = val)  
  
# function to view an expense information  
def viewExpenseInfo():  
    '''This function will display the expense information in the data frame'''  

    global data_table  
    global dateField, payee, category, amount, modeOfPayment  
  
    # If no record is selected
    if not data_table.selection():  
        mb.showerror('No record selected', 'Please select a record to view its details')  
  
    # Collecting the data from the selected row  
    currentExpense = data_table.item(data_table.focus())  
  
    # Store the values from the collected data in list  
    val = currentExpense['values']  
  
    # Get the date of expenditure from the list  
    expenditureDate = datetime.date(int(val[1][:4]), int(val[1][5:7]), int(val[1][8:]))  
  
    # Set the listed data in their respective entry fields  
    dateField.set_date(expenditureDate) ; payee.set(val[2]) ; category.set(val[3]) ; amount.set(val[4]) ; modeOfPayment.set(val[5])  
  
# function to clear the entries from the entry fields  
def clearFields():  
    '''This function will clear all the entries from the entry fields'''  

    global category, payee, amount, modeOfPayment, dateField, data_table  
  
    # Store today's date  
    todayDate = datetime.datetime.now().date()  
  
    # Reset to initial values  
    category.set('') ; payee.set('') ; amount.set(0.0) ; modeOfPayment.set(''), dateField.set_date(todayDate)  
    # Remove the specified item from the selection
    data_table.selection_remove(*data_table.selection())  
  
# function to delete the selected record  
def removeExpense():  
    '''This function will remove the selected record from the table'''  
  
    # If no record selected 
    if not data_table.selection():  
        mb.showerror('No record selected', 'Please select a record to delete')  
        return  
  
    currentExpense = data_table.item(data_table.focus())  
  
    # Store the values from the collected data in list  
    valuesSelected = currentExpense['values']  
  
    # Asking for confirmation
    confirmation = mb.askyesno('Are you sure?', f'Are you sure that you want to delete the record of {valuesSelected[2]}')  
  
    # SQL query to delete, if confirmed 
    if confirmation:  
        dbconnector.execute('DELETE FROM ExpenseTracker WHERE ID=%d' % valuesSelected[0])  
        dbconnector.commit()  
  
        # Display updated table 
        listAllExpenses()
  
# function to delete all the entries  
def removeAllExpenses():  
    '''This function will remove all the entries from the table'''  
      
    # Asking for confirmation  
    confirmation = mb.askyesno('Are you sure?', 'Are you sure that you want to delete all the expense items from the database?', icon='warning')  
  
    # SQL query to delete all, if confirmed 
    if confirmation:  
        data_table.delete(*data_table.get_children())  
  
        dbconnector.execute('DELETE FROM ExpenseTracker')  
        dbconnector.commit()  
  
        # Display updated table
        clearFields()  
        listAllExpenses()
  
# function to add an expense  
def addExpense():  
    '''This function will add an expense to the table and database'''  
  
    # using some global variables  
    global dateField, payee, category, amount, modeOfPayment  
    global dbconnector  
      
    # Display error if any field is empty
    if not dateField.get() or not payee.get() or not category.get() or not amount.get() or not modeOfPayment.get():  
        mb.showerror('Fields empty', "Please fill all the missing fields")  
    else:  
        # SQL query to insert expense  
        dbconnector.execute(  
            'INSERT INTO ExpenseTracker (Date, Payee, Category, Amount, ModeOfPayment) VALUES (?, ?, ?, ?, ?)',  
            (dateField.get_date(), payee.get(), category.get(), amount.get(), modeOfPayment.get())  
        )  
        dbconnector.commit()  
   
        # Display updated table
        clearFields()
        listAllExpenses()  
  
# function to edit the details of an expense  
def editExpense():  
    '''This function will allow user to edit the details of the selected expense'''  
 
    global data_table  
  
    # Update the details of the selected expense  
    def editExistingExpense():  
        '''This function will update the details of the selected expense in the database and table'''  
 
        global dateField, amount, category, payee, modeOfPayment  
        global dbconnector, data_table  
        
        currentExpense = data_table.item(data_table.focus())  
          
        # Store the values from the collected data in list  
        content = currentExpense['values']  
          
        # SQL query to update record 
        dbconnector.execute(  
            'UPDATE ExpenseTracker SET Date = ?, Payee = ?, Category = ?, Amount = ?, ModeOfPayment = ? WHERE ID = ?',  
            (dateField.get_date(), payee.get(), category.get(), amount.get(), modeOfPayment.get(), content[0])  
        )  
        dbconnector.commit()  
          
        # Display updated table
        clearFields()   
        listAllExpenses()  
 
        # Remove the edit button   
        editSelectedButton.destroy()  
          
    # If no record is selected
    if not data_table.selection():  
        mb.showerror('No expense selected', 'Please select an expense to edit')  
        return  
          
    # Display original information in the fields
    viewExpenseInfo()  
  
    # Change Add expense button to Edit expense button
    editSelectedButton = Button(  
        frameL2,  
        text = "Edit Expense",  
        font = ("Arial", "13"),  
        width = 30,  
        bg = "#90EE90",  
        fg = "#000000",  
        relief = GROOVE,  
        activebackground = "#008000",  
        activeforeground = "#98FB98",  
        command = editExistingExpense  
        )
  
    # Set the position of edit button
    editSelectedButton.grid(row = 0, column = 0, sticky = W, padx = 50, pady = 10)

# Function to view the monthly expenditure
def viewMonthlyExpenditure():
    # SQL query to get expenses by month
    monthly_data = dbconnector.execute('SELECT STRFTIME("%m-%Y", Date) AS Month, SUM(Amount) AS Expenditure \
                                       FROM ExpenseTracker GROUP BY STRFTIME("%m-%Y", Date) ORDER BY STRFTIME("%Y", Date);'
                                        )
    data = monthly_data.fetchall()
    # Create a sub-window to display monthly expenditure
    subwindow = Toplevel()
    subwindow.title('Monthly Expenditure')
    subwindow.config(width=300, height=500)
    tree = ttk.Treeview(subwindow, column=("Month", "Expenditure"), show='headings')
    tree.column("#1", anchor=CENTER)
    tree.heading("#1", text="Month")
    tree.column("#2", anchor=CENTER)
    tree.heading("#2", text="Expenditure")
    tree.pack()
    for row in data:
        tree.insert("", END, values=row)   
    
# Function to view category-wise expenditure
def viewCategoryExpenditure():
    # SQL query to get expenses by category
    category_data = dbconnector.execute('SELECT Category AS Category, SUM(Amount) AS Expenditure \
                                       FROM ExpenseTracker GROUP BY Category;'
                                        )
    data = category_data.fetchall()
    # Create a sub-window to display category-wise expenditure
    subwindow = Toplevel()
    subwindow.title('Category-wise Expenditure')
    subwindow.config(width=300, height=500)
    tree = ttk.Treeview(subwindow, column=("Category", "Expenditure"), show='headings')
    tree.column("#1", anchor=CENTER)
    tree.heading("#1", text="Category")
    tree.column("#2", anchor=CENTER)
    tree.heading("#2", text="Expenditure")
    tree.pack()
    for row in data:
        tree.insert("", END, values=row)   

if __name__ == "__main__":  
  
    # Connecting to the Database  
    dbconnector = sqlite3.connect("Database.db")
  
    # Create table when application starts if it doesn't already exist 
    dbconnector.execute(
        'CREATE TABLE IF NOT EXISTS ExpenseTracker (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, Date DATETIME, Payee TEXT, Category TEXT, Amount FLOAT, ModeOfPayment TEXT)'  
    )
    dbconnector.commit()
  
    # Creating the main window for application  

    window = Tk() 
    window.title("EXPENSE TRACKER")
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_x = (screen_width // 2) - (1415 // 2)
    window_y = (screen_height // 2) - (650 // 2)
    window.geometry(f"1415x650+{window_x}+{window_y}")
    window.resizable(False, False)
    window.config(bg = "#D3D3D3")
  
    # Creating frames for window structure
    frameLeft = Frame(window, bg = "#E5E4E2")  
    frameRight = Frame(window, bg = "#D3D3D3") 
    frameL1 = Frame(frameLeft, bg = "#E5E4E2")  
    frameL2 = Frame(frameLeft, bg = "#E5E4E2")  
    frameR1 = Frame(frameRight, bg = "#7393B3")  
    frameR2 = Frame(frameRight, bg = "#D3D3D3")
  
    # Set positions of the frames  
    frameLeft.pack(side=LEFT, fill = "both")  
    frameRight.pack(side = RIGHT, fill = "both", expand = True)  
    frameL1.pack(fill = "both")  
    frameL2.pack(fill = "both")  
    frameR1.pack(fill = "both")  
    frameR2.pack(fill = "both", expand = True)  
  
    # frameL1 frame 

    # Date Label  
    dateLabel = Label(  
        frameL1,  
        text = "Date:",  
        font = ("Arial", "11"),
        bg = "#E5E4E2",  
        fg = "#000000"  
        )  
  
    # Category Label  
    categoryLabel = Label(  
        frameL1,  
        text = "Category:",  
        font = ("Arial", "11"),
        bg = "#E5E4E2",  
        fg = "#000000"  
        )  
  
    # Amount Label  
    amountLabel = Label(  
        frameL1,  
        text = "Amount:",  
        font = ("Arial", "11"),
        bg = "#E5E4E2",  
        fg = "#000000"  
        )  
  
    # Payee Label  
    payeeLabel = Label(  
        frameL1,  
        text = "Payee:",  
        font = ("Arial", "11"),
        bg = "#E5E4E2",  
        fg = "#000000"  
        )  
  
    # Payment Mode Label  
    modeLabel = Label(  
        frameL1,  
        text = "Mode of Payment:",  
        font = ("Arial", "11"),
        bg = "#E5E4E2",  
        fg = "#000000"  
        )  
  
    # Setting positions of labels
    dateLabel.grid(row = 0, column = 0, sticky = W, padx = 10, pady = 10)      
    categoryLabel.grid(row = 1, column = 0, sticky = W, padx = 10, pady = 10)      
    amountLabel.grid(row = 2, column = 0, sticky = W, padx = 10, pady = 10)      
    payeeLabel.grid(row = 3, column = 0, sticky = W, padx = 10, pady = 10)      
    modeLabel.grid(row = 4, column = 0, sticky = W, padx = 10, pady = 10)      
  
    # Retrieving user entered data
    category = StringVar()  
    payee = StringVar()  
    modeOfPayment = StringVar()  
    amount = DoubleVar()  
  
    # Drop down calendar
    dateField = DateEntry(  
        frameL1,  
        date = datetime.datetime.now().date(),  
        font = ("Arial", "11"),  
        relief = GROOVE  
        )  

    # Category Field
    categoryField = OptionMenu(  
        frameL1,  
        category,  
        *['Food', 'Transport', 'Entertainment', 'Utilities', 'Other']
        )

    categoryField.config(  
        width = 15,  
        font = ("Arial", "11"),  
        relief = GROOVE,  
        bg = "#FFFFFF"  
        )  
  
    # Amount Field
    amountField = Entry(  
        frameL1,  
        text = amount,  
        width = 20,  
        font = ("Arial", "11"),  
        bg = "#FFFFFF",  
        fg = "#000000",  
        relief = GROOVE  
        )  
  
    # Payee information Field
    payeeField = Entry(  
        frameL1,  
        text = payee,  
        width = 20,  
        font = ("Arial", "11"),  
        bg = "#FFFFFF",  
        fg = "#000000",  
        relief = GROOVE  
        )  
  
    # Drop down for selecting mode of payment  
    modeField = OptionMenu(  
        frameL1,  
        modeOfPayment,  
        *['Cash', 'Cheque', 'Credit Card', 'Debit Card', 'UPI']  
        )  

    modeField.config(  
        width = 15,  
        font = ("Arial", "11"),  
        relief = GROOVE,  
        bg = "#FFFFFF"  
        )  
  
    # Setting positions of fields
    dateField.grid(row = 0, column = 1, sticky = W, padx = 10, pady = 10)  
    categoryField.grid(row = 1, column = 1, sticky = W, padx = 10, pady = 10)  
    amountField.grid(row = 2, column = 1, sticky = W, padx = 10, pady = 10)  
    payeeField.grid(row = 3, column = 1, sticky = W, padx = 10, pady = 10)  
    modeField.grid(row = 4, column = 1, sticky = W, padx = 10, pady = 10)  
  
    # frameL2 frame
 
    # insert button  
    insertButton = Button(  
        frameL2,  
        text = "Add Expense",  
        font = ("Arial", "13"),  
        width = 30,  
        bg = "#90EE90",  
        fg = "#000000",  
        relief = GROOVE,  
        activebackground = "#008000",  
        activeforeground = "#98FB98",  
        command = addExpense  
        )
  
    # reset button  
    resetButton = Button(  
        frameL2,  
        text = "Reset the fields",  
        font = ("Arial", "13"),  
        width = 30,  
        bg = "#FF0000",  
        fg = "#FFFFFF",  
        relief = GROOVE,  
        activebackground = "#8B0000",  
        activeforeground = "#FFB4B4",  
        command = clearFields  
        )  
  
    # Setting positions of buttons
    insertButton.grid(row = 0, column = 0, sticky = W, padx = 50, pady = 10) 
    resetButton.grid(row = 1, column = 0, sticky = W, padx = 50, pady = 10)  
  
    # frameR1 frame
 
    # View Button  
    viewButton = Button(  
        frameR1,  
        text = "View Selected Expense",  
        font = ("Arial", "13"),  
        width = 35,  
        bg = "#E5E4E2",  
        fg = "#000000",  
        relief = GROOVE,  
        activebackground = "#C0C0C0",  
        activeforeground = "#FFF8DC",  
        command = viewExpenseInfo  
        )  
  
    # Edit Button  
    editButton = Button(  
        frameR1,  
        text = "Edit Selected Expense",  
        font = ("Arial", "13"),  
        width = 35,  
        bg = "#E5E4E2",  
        fg = "#000000",  
        relief = GROOVE,  
        activebackground = "#C0C0C0",  
        activeforeground = "#FFF8DC",  
        command = editExpense  
        )
  
    # Delete Button  
    deleteButton = Button(  
        frameR1,  
        text = "Delete Selected Expense",  
        font = ("Arial", "13"),  
        width = 35,  
        bg = "#E5E4E2",  
        fg = "#000000",  
        relief = GROOVE,  
        activebackground = "#C0C0C0",  
        activeforeground = "#FFF8DC",  
        command = removeExpense  
        )  
      
    # Delete All Button  
    deleteAllButton = Button(  
        frameR1,  
        text = "Delete All Expense",  
        font = ("Arial", "13"),  
        width = 35,  
        bg = "#E5E4E2",  
        fg = "#000000",  
        relief = GROOVE,  
        activebackground = "#C0C0C0",  
        activeforeground = "#FFF8DC",  
        command = removeAllExpenses  
        )  
    
    # Monthly Expenditure Button
    monthlyExpenditureButton = Button(
        frameR1,
        text = "View Monthly Expenditure",
        font = ("Arial", "13"),  
        width = 35,  
        bg = "#E5E4E2",  
        fg = "#000000",  
        relief = GROOVE,  
        activebackground = "#C0C0C0",  
        activeforeground = "#FFF8DC",  
        command = viewMonthlyExpenditure
        )
    
    # Category-wise Expenditure Button
    categoryExpenditureButton = Button(
        frameR1,
        text = "View Category-wise Expenditure",
        font = ("Arial", "13"),  
        width = 35,  
        bg = "#E5E4E2",
        fg = "#000000",  
        relief = GROOVE,  
        activebackground = "#C0C0C0",  
        activeforeground = "#FFF8DC",  
        command = viewCategoryExpenditure
        )

  
    # Setting positions of buttons 
    viewButton.grid(row = 0, column = 0, sticky = W, padx = 10, pady = 10)  
    editButton.grid(row = 0, column = 1, sticky = W, padx = 10, pady = 10)
    monthlyExpenditureButton.grid(row = 0, column = 2, sticky = W, padx = 10, pady = 10)
    deleteButton.grid(row = 1, column = 0, sticky = W, padx = 10, pady = 10)  
    deleteAllButton.grid(row = 1, column = 1, sticky = W, padx = 10, pady = 10)
    categoryExpenditureButton.grid(row = 1, column = 2, sticky = W, padx = 10, pady = 10)
  
    # frameR2 frame
  
    # creating a table to display all the entries  
    data_table = ttk.Treeview(  
        frameR2,  
        selectmode = BROWSE,  
        columns = ('ID', 'Date', 'Payee', 'Category', 'Amount', 'Mode of Payment')  
        )
      
    # creating a vertical scrollbar to the data table  
    scrollbar = Scrollbar(  
        data_table,  
        orient = VERTICAL,  
        command = data_table.yview  
        )  
  
    # Set the position of the scrollbar
    scrollbar.pack(side = RIGHT, fill = Y) 
    data_table.config(yscrollcommand = scrollbar.set)  
  
    # Adding headings to table  
    data_table.heading('ID', text = 'S No.', anchor = CENTER)  
    data_table.heading('Date', text = 'Date', anchor = CENTER)  
    data_table.heading('Payee', text = 'Payee', anchor = CENTER)  
    data_table.heading('Category', text = 'Category', anchor = CENTER)  
    data_table.heading('Amount', text = 'Amount', anchor = CENTER)  
    data_table.heading('Mode of Payment', text = 'Mode of Payment', anchor = CENTER)  
  
    # Add columns to table  
    data_table.column('#0', width = 0, stretch = NO)  
    data_table.column('#1', width = 50, stretch = NO)  
    data_table.column('#2', width = 200, stretch = NO)  
    data_table.column('#3', width = 200, stretch = NO)  
    data_table.column('#4', width = 200, stretch = NO)  
    data_table.column('#5', width = 200, stretch = NO)  
    data_table.column('#6', width = 150, stretch = NO)  
  
    # Set the position of the table on the main window 
    data_table.place(relx = 0, y = 0, relheight = 1, relwidth = 1)
    
    # List all previous expenses when application is started
    listAllExpenses()

    window.mainloop()  