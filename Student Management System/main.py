import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename,askdirectory
from PIL import Image,ImageTk,ImageDraw,ImageFont,ImageOps
from io import BytesIO
import re
import random
import sqlite3
import os
import win32api
import smtplib#enable to send email
from email.mime.multipart import MIMEMultipart
from email.mime.text import  MIMEText
import  my_email
from tkinter.ttk import Combobox,Treeview


root = tk.Tk()
root.geometry("500x600+500+100")
root.resizable(width=False,height=False)
root.title("Student Management & Registration System")
#we create a color variable since it will be used most of the time
bg_color = "#273b7a"
#load icons
login_student_icon = tk.PhotoImage(file="images/login_student_img.png")
login_admin_icon = tk.PhotoImage(file="images/admin_img.png")
add_student_icon = tk.PhotoImage(file="images/add_student_img.png")
locked_icon = tk.PhotoImage(file="images/locked.png")
unlock_icon = tk.PhotoImage(file="images/unlocked.png")
add_student_pic = tk.PhotoImage(file="images/add_image.png")

#creation of sqllite database
def init_database():
    if os.path.exists("students_accounts.db"):
        connection = sqlite3.connect("students_accounts.db")
        cursor = connection.cursor()  # will help us to excute sql queries also to fecht data from database
        cursor.execute(""" SELECT *  FROM data  """)  # it will excute every sql queries

        connection.commit()  # will commit transaction with database
        #print(cursor.fetchall())
        connection.close()  # will close the database connection
    else:
        connection = sqlite3.connect("students_accounts.db")
        cursor = connection.cursor()#will help us to excute sql queries also to fecht data from database
        cursor.execute("""
        CREATE TABLE data(id_number text,password text,
        name text,age text,
        gender text,phone_number text,
        student_class text,email text,
        image blob)
        """)#it will excute every sql queries

        connection.commit()#will commit transaction with database
        connection.close()#will close the database connection
#create a function that will add student to database
def add_data(id_number,password,name,age, gender,phone_number,student_class,email ,image):
    connection = sqlite3.connect("students_accounts.db")
    cursor = connection.cursor()  # will help us to execute sql queries also to fecht data from database
    cursor.execute("""
    INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (id_number, password, name, age, gender, phone_number, student_class, email, image))
  # it will execute every sql queries

    connection.commit()  # will commit transaction with database
    connection.close()  # will close the database connection
#creating a confirmation box
# Function to check if ID number already exists in the database
def check_id_already_exists(id_number):
    connection = sqlite3.connect("students_accounts.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id_number FROM data WHERE id_number=?", (id_number,))
    result = cursor.fetchone()
    connection.close()
    return result is not None
def check_valid_password(id_number,password):
    connection = sqlite3.connect("students_accounts.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id_number,password FROM data WHERE id_number=? AND password =?", (id_number,password))
    result = cursor.fetchone()
    connection.close()
    return result is not None
def confirmation_box(message):
    # create a function for cancel and yes confirmation
    answer = tk.BooleanVar()  # return either True or False Value
    answer.set(False)

    def action(ans):
        answer.set(ans)
        confirm_fm.destroy()
    confirm_fm = tk.Frame(root,highlightbackground=bg_color, highlightthickness=3)
    message_lb = tk.Label(confirm_fm, text=message, font=('Bold', 15))
    message_lb.pack(pady=20)
    cancel_btn = tk.Button(confirm_fm, text="Cancel", font=('Bold', 15), bg=bg_color, fg="white", relief="sunken",command=lambda:action(False))
    cancel_btn.place(x=50, y=160)
    yes_btn = tk.Button(confirm_fm, text="Yes", font=('Bold', 15), bg=bg_color, fg="white", relief="sunken",command=lambda:action(True))
    yes_btn.place(x=190, y=160, width=80)
    confirm_fm.place(x=100,y=120,width=320,height=220)
    #create wait_window function tha allow us to keep windos open till a button is clicked
    #print("this line will executes:55")
    root.wait_window(confirm_fm)
    #print("this line will be executed after the wait_window fun finish to run ")
    return answer.get()
def message_box(message):
    message_box_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)
    message_box_fm.place(x=100,y=120,width=320,height =200)
    close_btn = tk.Button(message_box_fm,text='X',bd=0,font=('Bold',13),fg=bg_color,command=lambda :message_box_fm.destroy())
    close_btn.place(x=290,y=5)
    message_lb = tk.Label(message_box_fm,text=message,font=('Bold',15))
    message_lb.pack(pady=50)
#create a function to draw student card
def draw_student_card(student_pic_path,student_data):
    labels = """
    ID Number:
    Name :
    Gender:
    Age :
    Class:
    Contact:
    Email:
    """

    student_card = Image.open("images/student_card_frame.png")
    pic = Image.open(student_pic_path).resize((100,100))

    student_card.paste(pic,(15,25))
    draw = ImageDraw.Draw(student_card)
    heading_foot =ImageFont.truetype('times',18)
    labels_font = ImageFont.truetype('arial',15)
    data_foot = ImageFont.truetype('times', 18)
    draw.text(xy=(150,60),text='Student Card',fill=(0,0,0),font=heading_foot)
    draw.multiline_text(xy=(15,120),text=labels,fill=(0,0,0),font=labels_font,spacing=7)
    draw.multiline_text(xy=(95,120),text=student_data,fill=(0,0,0),font=data_foot,spacing=3)
    return student_card

#create a function to display student card
def student_card_page(student_card_obj,bypass_login_page=False):
#function used to save an image
    def sava_student_card():
        path = askdirectory()

        if path:


             student_card_obj.save(f'{path}/student_card.png')
    def print_student_card():

        path = askdirectory()

        if path:

            student_card_obj.save(f'{path}/student_card.png')
            #after installing pywin32 for printinf and various function
            #now we want to print
            win32api.ShellExecute(0, 'print',f'{path}/student_card.png',None,'.',0)

    def close_page():
            student_card_fm.destroy()

            if not bypass_login_page:
                root.update()
                login_student_page()

    student_card_img = ImageTk.PhotoImage(student_card_obj)
    student_card_fm = tk.Frame(root,highlightbackground=bg_color, highlightthickness=3)
    heading_lb = tk.Label(student_card_fm,text="student card",bg=bg_color,fg="white",font=("bold",18))
    heading_lb.place(x=0,y=0,width=400)

    close_btn = tk.Button(student_card_fm,text="X",bg=bg_color,
                          fg="white",font=('bold',13),bd=0,
                          command= close_page)
    #card_img =ImageTk.PhotoImage(Image.open('card.png'))
    close_btn.place(x=370,y=0)
    student_card_lb = tk.Label(student_card_fm,image=student_card_img)
    student_card_lb.place(x=50,y=50)
    student_card_lb.image = student_card_img

    #student_card_lb.image = card_img

    save_student_card_btn = tk.Button(student_card_fm,text='sava student card',
                                      bg=bg_color,fg='white',font=('bold',15),bd=1,command=  sava_student_card)
    save_student_card_btn.place(x=80,y=375)

    print_student_card_btn = tk.Button(student_card_fm,text='🖨️',
                                      bg=bg_color,fg='white',font=('bold',18),bd=1,command= print_student_card)
    print_student_card_btn.place(x=270,y=370)
    student_card_fm.place(x=50,y=30,width=400,height=490)


#create a function to call welcome page first phase
def welcom_page():
    def forward_to_student_login_page():
        welcome_page.destroy()
        root.update()
        login_student_page()

    def forward_to_admin_login_page():
            welcome_page.destroy()
            root.update()
            admin_login_page()
    def move_to_addd_account_page():
        welcome_page.destroy()
        root.update()
        add_account_page()

    # creation of the welcome frame
    welcome_page = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)
    heeading_lb = tk.Label(welcome_page, text="Welcome to Student Registration\n && Management System ",
                           bg=bg_color, fg="white", font=("bold", 18))
    heeading_lb.place(x=0, y=0, width=400)
    # creating a buttons for student log in
    student_login_btn = tk.Button(welcome_page, text="Login Student", bg=bg_color, fg="white", font=("bold", 15), bd=0,command=forward_to_student_login_page)
    student_login_btn.place(x=120, y=125, width=200)
    # inser icon before label for admin log in
    student_login_img = tk.Button(welcome_page, image=login_student_icon, bd=0,command=forward_to_student_login_page)
    student_login_img.place(x=60, y=100)

    # creating a buttons for crating a studnet account
    admin_login_btn = tk.Button(welcome_page, text="Login Admin", bg=bg_color, fg="white", font=("bold", 15), bd=0,command= forward_to_admin_login_page)
    admin_login_btn.place(x=120, y=225, width=200)
    # inser icon before label
    admin_login_img = tk.Button(welcome_page, image=login_admin_icon, bd=0,command= forward_to_admin_login_page)
    admin_login_img.place(x=60, y=200)

    # creating a buttons
    add_student_login_btn = tk.Button(welcome_page, text="Create Account", bg=bg_color, fg="white", font=("bold", 15),
                                      bd=0,command=move_to_addd_account_page)
    add_student_login_btn.place(x=120, y=325, width=200)
    # inser icon before label
    add_student_login_img = tk.Button(welcome_page, image=add_student_icon, bd=0)
    add_student_login_img.place(x=60, y=300)

    welcome_page.pack(pady=30)
    welcome_page.pack_propagate(False)
    welcome_page.configure(width=400, height=420)
#the function for forgetting password

#create a function that can send the Email to the Email Address of a student
def sendmail_to_student(email,message,subject):
    smtp_serve = 'smtp.gmail.com' #its a smtp  server address witch is provided by google to send Email messages using gmail account
    smtp_port = 587 #this is the port and we smtp is the protocole

    username = my_email.email_address
    password = my_email.passord

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = username
    msg ['To'] = email

    msg.attach(MIMEText(_text=message, _subtype='html'))

    smtp_connection = smtplib.SMTP(host=smtp_serve, port=smtp_port)
    smtp_connection.starttls()
    smtp_connection.login(user=username, password=password)
    smtp_connection.sendmail(from_addr=username, to_addrs=email,msg=msg.as_string())

def forget_page_password():

#the function for recovering password
    def recover_password():
        if check_id_already_exists( id_number=student_id_ent.get()):
            #print("Correct ID")
            #once the ID Number is correct now we can process to recover
            connection = sqlite3.connect("students_accounts.db")
            cursor = connection.cursor()
            cursor.execute(f"""
            SELECT password FROM data WHERE id_number == '{student_id_ent.get()}'
            
            """)
            connection.commit()
            recover_password = cursor.fetchall()[0][0]
            cursor.execute(f"""
                        SELECT email FROM data WHERE id_number == '{student_id_ent.get()}'

                        """)
            connection.commit()
            student_email = cursor.fetchall()[0][0]
            connection.close()

            confirmation = confirmation_box(message=f""" We will send\n Your Forget Password
via Your Email Address:
{student_email}
 Do you want to continue?
             """)
            #if the student press yes it means the student want to recover the password
            if confirmation:
                msg = f"""
                <h2> {recover_password}</h2>
                <p> once Remember Your Password, After Delete this Message</p>"""
                sendmail_to_student(email=student_email, message=msg,subject='password Recovery')

        else:
            #the user must provide the correct ID Number
            #print('Incorrect ID')
            message_box(message='! invalid ID Number')

    forget_page_password_fm = tk.Frame(root,highlightbackground=bg_color, highlightthickness=3)
    heading_lb = tk.Label(forget_page_password_fm, text="⚠️Forgetting Password",
                          font=('Bold', 15), bg=bg_color,fg='white')
    heading_lb.place(x=0, y=0, width=350)
    close_btn = tk.Button(forget_page_password_fm,text="X",bg=bg_color,
                          fg="white",font=('bold',13),bd=0,
                          command=lambda :forget_page_password_fm.destroy())
    close_btn.place(x=320,y=0)
    student_id_lb = tk.Label(forget_page_password_fm,text="Enter Student ID Number",font=('bold',13))
    student_id_lb.place(x=70,y=40)
    student_id_ent = tk.Entry(forget_page_password_fm,font=('Bold',15),justify=tk.CENTER)
    student_id_ent.place(x=70,y=70, width=180)
    info_lb = tk.Label(forget_page_password_fm,text="""Via Your Email Address 
we will send to you
Your Forgot Password. """,font=('bold',10),justify=tk.LEFT)
    info_lb.place(x=75,y=110)
    next_btn = tk.Button(forget_page_password_fm,text="Next",font=('bold',13),bg=bg_color,fg="white",command=recover_password)
    next_btn.place(x=130,y=200,width=80)

    forget_page_password_fm.place(x=75,y=120,width=350,height=250)


#to fetch data from the database to display on the home page

def fetch_student_data(query):
    connection = sqlite3.connect('students_accounts.db')
    cursor = connection.cursor()

    cursor.execute(query)

    connection.commit()
    response = cursor.fetchall()
    connection.close()

    return response


#create a student dashboard
def student_dashboard(student_id):
    dashboard_fm = tk.Frame(root,highlightbackground=bg_color,highlightthickness=3)
    options_fm = tk.Frame(dashboard_fm,highlightbackground=bg_color,highlightthickness=3,bg='gray')
    get_student_details = fetch_student_data(f"""
    SELECT name,age,gender,student_class,phone_number,email FROM data WHERE id_number == '{student_id}'
    
    """)
    get_student_pic = fetch_student_data(f"""
        SELECT image FROM data WHERE id_number == '{student_id}'

        """)

    student_pic = BytesIO(get_student_pic[0][0])




    def home_page():
        pic_img_obj = ImageTk.PhotoImage(Image.open(student_pic))
        home_frame = tk.Frame(pages_fm,)
        student_pic_lb = tk.Label(home_frame,image=pic_img_obj)
        student_pic_lb.image = pic_img_obj
        student_pic_lb.place(x=10,y=10)

        hi_lb = tk.Label(home_frame,text=f'!Hi {get_student_details[0][0]}',font=('Bold',15))
        hi_lb.place(x=130,y=50)
        student_details = f"""
Student ID: {student_id}\n
Name: {get_student_details[0][0]}\n
Age: {get_student_details[0][1]}\n
Gender: {get_student_details[0][2]}\n
Class: {get_student_details[0][3]}\n
Contact: {get_student_details[0][4]}\n
Email: {get_student_details[0][5]}
 """
        student_details_lb = tk.Label(home_frame,text=student_details,font=('bold',13),justify=tk.LEFT)
        student_details_lb.place(x=20,y=110)

        home_frame.pack(fill=tk.BOTH,expand=True)

    def student_card():
        student_details = f"""
    {student_id}
{get_student_details[0][0]}
{get_student_details[0][2]}
{get_student_details[0][1]}
{get_student_details[0][3]}
{get_student_details[0][4]}
{get_student_details[0][5]}
         """
        student_card_image_obj = draw_student_card(student_pic_path=student_pic,student_data=student_details)
        student_card_imgs = ImageTk.PhotoImage(student_card_image_obj)

        # function used to save an image
        def sava_student_card():
            path = askdirectory()

            if path:
                student_card_image_obj.save(f'{path}/student_card.png')

        def print_student_card():

            path = askdirectory()

            if path:
                student_card_image_obj.save(f'{path}/student_card.png')
                # after installing pywin32 for printinf and various function
                # now we want to print
                win32api.ShellExecute(0, 'print', f'{path}/student_card.png', None, '.', 0)


        student_frame = tk.Frame(pages_fm)

        card_lb = tk.Label(student_frame,image=student_card_imgs)
        card_lb.image = student_card_imgs
        card_lb.place(x=20,y=50)

        save_student_card_btn = tk.Button(student_frame, text='sava student card',
                                          bg=bg_color, fg='white', font=('bold', 15), bd=1,command=sava_student_card)
        save_student_card_btn.place(x=40, y=400)

        print_student_card_btn = tk.Button(student_frame, text='🖨️',
                                           bg=bg_color, fg='white', font=('bold', 15), bd=1,command=print_student_card)
        print_student_card_btn.place(x=240, y=400)

        student_frame.pack(fill=tk.BOTH, expand=True)

    def security():
        def show_hide_password():
            if current_password_ent['show'] == "*":
                current_password_ent.config(show='')
                show_hide_btn.config(image=unlock_icon)
            else:
                current_password_ent.config(show='*')
                show_hide_btn.config(image=locked_icon)
        def set_password():
            if new_password_ent.get() != '':
                confirm = confirmation_box(message="Do You Want to\nYour Current Password")
                if confirm:
                    connection = sqlite3.connect('students_accounts.db')

                    cursor = connection.cursor()
                    cursor.execute(f"""
                    UPDATE data SET password = '{new_password_ent.get()}' WHERE id_number == '{student_id}' 
""")
                    connection.commit()
                    connection.close()
                    message_box(message='Password Changed Successfully')

                    current_password_ent.config(state=tk.NORMAL)
                    current_password_ent.delete(0,tk.END)
                    current_password_ent.insert(0,new_password_ent.get())
                    current_password_ent.config(state='readonly')

                    new_password_ent.delete(0,tk.END)
            else:
                message_box(message="Enter New Password Required")
        security_frame = tk.Frame(pages_fm)
        current_password_lb = tk.Label(security_frame,text="Your Current Password",
                                       font=('bold',12))
        current_password_lb.place(x=80,y=30)

        current_password_ent = tk.Entry(security_frame,font=('bold',15),justify=tk.CENTER,show="*")
        current_password_ent.place(x=50,y=80)
        student_current_password = fetch_student_data(f"""
        SELECT password FROM data WHERE id_number == '{student_id}'
        """)
        current_password_ent.insert(tk.END, student_current_password[0][0])
        current_password_ent.config(state='readonly')

        change_password_lb = tk.Label(security_frame,text="Change Password",font=("bold",15),bg='red',fg='white')
        change_password_lb.place(x=30, y=210,width=290)

        new_password_lb = tk.Label(security_frame,text='Set New Password',font=('bold',12))
        new_password_lb.place(x=100,y=260)

        new_password_ent = tk.Entry(security_frame, font=('bold', 15),justify=tk.CENTER)
        new_password_ent.place(x=60, y=330)

        change_password_btn = tk.Button(security_frame,text='Set Password',
                                        font=('bold',12),bg=bg_color,fg="white",command=set_password)
        change_password_btn.place(x=110,y=380)


        show_hide_btn = tk.Button(security_frame, image=locked_icon, bd=0, command=show_hide_password)
        show_hide_btn.place(x=280, y=70)

        security_frame.pack(fill=tk.BOTH, expand=True)

    def edit_data():
        edit_frame = tk.Frame(pages_fm)

        pic_path = tk.StringVar()
        pic_path.set('')

        def open_pic():
            path = askopenfilename()
            if path:
                img = ImageTk.PhotoImage(Image.open(path).resize((100, 100)))
                # this pic_path willl help us to pictures to the database
                pic_path.set(path)

                add_pic_btn.config(image=img)
                add_pic_btn.image = img

        def remove_highlight_warning(entry):
            if entry['highlightbackground'] != 'gray':
                if entry.get() != '':
                    entry.config(highlightbackground="gray", highlightcolor=bg_color)

        def check_invalid_email(email):
            # using this pattern we will check email address format
            pattern = "^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$"
            match = re.match(pattern=pattern, string=email)
            return match

        def check_input():
            nonlocal get_student_details,get_student_pic,student_pic
            if student_name_en.get() == '':
                student_name_en.config(highlightbackground="red", highlightcolor='red')
                student_name_en.focus()
                message_box(message='Student Full Name Is Required')
            elif student_age_en.get() == '':
                student_age_en.config(highlightbackground="red", highlightcolor='red')
                student_age_en.focus()
                message_box(message='Student Age Is Required')
            elif student_contact_en.get() == '':
                student_contact_en.config(highlightbackground="red", highlightcolor='red')
                student_contact_en.focus()
                message_box(message='Student Contact Is Required')
            elif student_class_btn.get() == '':
                student_class_btn.focus()
                message_box(message='Select Student Class Is Required')
            elif student_email_en.get() == '':
                student_email_en.config(highlightbackground="red", highlightcolor='red')
                student_email_en.focus()
                message_box(message='Student Email Is Required')
            elif not check_invalid_email(email=student_email_en.get().lower()):
                student_email_en.config(highlightcolor="red", highlightbackground='red')
                student_email_en.focus()
                message_box(message="Please Enter a Valid\nEmail Address")

            else:
                image = b''
                if pic_path.get() != '':
                    new_student_pic = Image.open(pic_path.get()).resize((100, 100))
                    new_student_pic.save('temp_pic.png')

                    with  open('temp_pic.png', 'rb') as read_new_pic:
                        new_picture_binary = read_new_pic.read()
                        read_new_pic.close()
                    connection =sqlite3.connect('students_accounts.db')
                    cursor = connection.cursor()

                    cursor.execute(f"""
                    UPDATE data SET image=? WHERE id_number == '{student_id}'
                    """,[new_picture_binary])

                    connection.commit()
                    connection.close()
                    message_box(message='Data Successfully Update')

                name = student_name_en.get()
                age = student_age_en.get()
                selected_class = student_class_btn.get()
                contact_number = student_contact_en.get()
                email_address = student_email_en.get()

                connection = sqlite3.connect('students_accounts.db')
                cursor = connection.cursor()

                cursor.execute(f"""
                    UPDATE data SET name ='{name}',age ='{age}', student_class='{selected_class}',Phone_number='{contact_number}'
                    ,email = '{email_address}' WHERE id_number == '{student_id}'
                     """)

                connection.commit()
                connection.close()

                get_student_details = fetch_student_data(f"""
                   SELECT name,age,gender,student_class,phone_number,email FROM data WHERE id_number == '{student_id}'

                   """)
                get_student_pic = fetch_student_data(f"""
                       SELECT image FROM data WHERE id_number == '{student_id}'

                       """)

                student_pic = BytesIO(get_student_pic[0][0])

                message_box(message='Data Successfully Update')

        student_current_pic = ImageTk.PhotoImage(Image.open(student_pic))

        add_pic_fm = tk.Frame(edit_frame, highlightbackground=bg_color, highlightthickness=2)
        add_pic_btn = tk.Button(add_pic_fm, image= student_current_pic,
                                bd=0, command=open_pic)
        add_pic_btn.image = student_current_pic

        add_pic_btn.pack()
        add_pic_fm.place(x=5, y=5, width=105, height=105)
        #name
        student_name_lb = tk.Label(edit_frame, text="Student Full Name", font=("bold", 12))
        student_name_lb.place(x=5, y=130)
        student_name_en = tk.Entry(edit_frame, font=("bold", 15)
                                   , highlightbackground="gray", highlightthickness=2, highlightcolor=bg_color)
        student_name_en.place(x=5, y=160, width=180)
        # creating a bind to mage the color afet and before entering the data

        student_name_en.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_name_en))
        student_name_en.insert(tk.END, get_student_details[0][0])

        #Age
        student_age_lb = tk.Label(edit_frame, text="Student Age", font=("bold", 12))
        student_age_lb.place(x=5, y=200)
        student_age_en = tk.Entry(edit_frame, font=("bold", 15)
                                  , highlightbackground="gray", highlightthickness=2, highlightcolor=bg_color)
        student_age_en.place(x=5, y=230, width=180)
        student_age_en.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_age_en))
        student_age_en.insert(tk.END, get_student_details[0][1])

        #Contact
        student_contact_lb = tk.Label(edit_frame, text="Contact Phone Number", font=("bold", 12))
        student_contact_lb.place(x=4, y=270)
        student_contact_en = tk.Entry(edit_frame, font=("bold", 15)
                                      , highlightbackground="gray", highlightthickness=2, highlightcolor=bg_color)
        student_contact_en.place(x=5, y=300, width=180)
        student_contact_en.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_contact_en))
        student_contact_en.insert(tk.END, get_student_details[0][4])

        #class
        select_student_lb = tk.Label(edit_frame, text="Student Class ", font=("bold", 12))
        select_student_lb.place(x=5, y=340)
        student_class_btn = ttk.Combobox(edit_frame, font=("bold", 15), state='readonly', values=class_list)
        student_class_btn.place(x=5, y=370, width=180, height=30)
        student_class_btn.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_class_btn))
        student_class_btn.set(get_student_details[0][3])
        #email
        student_email_lb = tk.Label(edit_frame, text="Student Email Address", font=("bold", 12))
        student_email_lb.place(x=5, y=400)
        student_email_en = tk.Entry(edit_frame, font=("Bold", 15) , highlightbackground="gray", highlightthickness=2, highlightcolor=bg_color)
        student_email_en.place(x=5, y=430, width=200)
        student_email_en.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_email_en))
        student_email_en.insert(tk.END, get_student_details[0][5])
        #button update
        update_btn = tk.Button(edit_frame,text="Update",font=('bold',15),fg='white',bg=bg_color,bd=0,command= check_input)
        update_btn.place(x=220,y=430,width=80)


        edit_frame.pack(fill=tk.BOTH, expand=True)

    def delete():
        def confirm_delete_account():
            confirm = confirmation_box(message="⚠️Do You Want To Delete\nYour Account")
            if confirm:
                connection = sqlite3.connect('students_accounts.db')
                cursor = connection.cursor()

                cursor.execute(f"""
                DELETE FROM data WHERE id_number == '{student_id}'
                """)
                connection.commit()
                connection.close()

                dashboard_fm.destroy()
                welcom_page()
                root.update()
                message_box(message="Account Successfully Deleted!")
        delete_account_frame = tk.Frame(pages_fm)
        delete_account_lb = tk.Label(delete_account_frame,text='⚠️Delete Account',
                                     bg='red',fg='white',font=("bold",15))
        delete_account_lb.place(x=30,y=100,width=290)

        delete_account_btn = tk.Button(delete_account_frame,
                                       text="DELETE Account", bg='red',fg='white',font=("bold",15),command=confirm_delete_account)
        delete_account_btn.place(x=110,y=200)


        delete_account_frame.pack(fill=tk.BOTH, expand=True)
    def logout():

        confirm = confirmation_box(message="Do You Want to\nLogout Your Account")

        if confirm:
            dashboard_fm.destroy()
            welcom_page()
            root.update()


    pages_fm = tk.Frame(dashboard_fm, bg="white")
    pages_fm.place(x=122, y=5, width=350, height=570)
    home_page()

    def switch(indicate,page):
        home_indicate.config(bg="gray")
        student_card_indicate.config(bg="gray")
        security_indicate.config(bg="gray")
        edit_data_indicate.config(bg="gray")
        delete_indicate.config(bg="gray")

        indicate.config(bg=bg_color)

        for child in pages_fm.winfo_children():
            child.destroy()
            root.update()
        page()

    #def indicate(lb, page):

        #lb.config(bg="black")
        #delete_pages()
        #page()

    btn_home = tk.Button(options_fm, text="Home", font=("bold", 15),
                         fg=bg_color, bd=0, bg="gray",justify=tk.LEFT, command=lambda: switch(indicate=home_indicate,page=home_page))
    btn_home.place(x=10, y=50)
    # indicate lable for home page button
    home_indicate = tk.Label(options_fm, text="", bg=bg_color)
    home_indicate.place(x=5, y=48, width=3, height=40)
    # student card batton
    btn_student_card = tk.Button(options_fm, text="Student\nCard", font=("bold", 15),
                         fg=bg_color, bd=0, bg="gray",justify=tk.LEFT, command=lambda: switch(indicate=student_card_indicate,page=student_card))
    btn_student_card.place(x=10, y=100)
    # student card indicate
    student_card_indicate = tk.Label(options_fm, text="", bg="gray")
    student_card_indicate.place(x=5, y=108, width=3, height=40)
    # security button
    btn_security = tk.Button(options_fm, text="Security", font=("bold", 15),
                            fg=bg_color, bd=0, bg="gray",justify=tk.LEFT, command=lambda: switch(indicate=security_indicate,page=security))
    btn_security.place(x=10, y=170)
    # security indicate
    security_indicate = tk.Label(options_fm, text="", bg="gray")
    security_indicate.place(x=5, y=170, width=3, height=40)
    # Edit Data button
    btn_edit_data = tk.Button(options_fm, text="Edit Data", font=("bold", 15),
                          fg=bg_color, bd=0, bg="gray", command=lambda: switch(indicate=edit_data_indicate,page=edit_data))
    btn_edit_data.place(x=10, y=220)
    # Edit Data indicate
    edit_data_indicate = tk.Label(options_fm, text="", bg="gray")
    edit_data_indicate.place(x=5, y=220, width=3, height=40)

    # Delete Account button
    btn_delete_account = tk.Button(options_fm, text="Delete\nAccount", font=("bold", 15),
                              fg=bg_color, bd=0, bg="gray",justify=tk.LEFT, command=lambda: switch(indicate=delete_indicate,page=delete))
    btn_delete_account.place(x=10, y=270)
    # delete Account indicate
    delete_indicate = tk.Label(options_fm, text="", bg="gray")
    delete_indicate.place(x=5, y=280, width=3, height=40)

    # logout button
    btn_logout = tk.Button(options_fm, text="Logout", font=("bold", 15),
                                   fg=bg_color, bd=0, bg="gray",command=logout)
    btn_logout.place(x=10, y=340)

    options_fm.place(x=0, y=0, width=120, height=575)



    dashboard_fm.pack(pady=5)
    dashboard_fm.pack_propagate(False)
    dashboard_fm.configure(width=480, height=580)

def login_student_page():
    def show_hide_password():
        if password_ent['show'] == "*":
            password_ent.config(show='')
            show_hide_btn.config(image=unlock_icon)
        else:
            password_ent.config(show='*')
            show_hide_btn.config(image=locked_icon)
    def forward_to_welcome_page():
        student_login_page_fm.destroy()
        root.update()
        welcom_page()

    def remove_highlight_warning(entry):
        if entry['highlightbackground'] != 'gray':
            if entry.get() != '':
                entry.config(highlightbackground="gray", highlightcolor=bg_color)

    def login_account():   #checking id number and password validation
        verify_id_number =  check_id_already_exists(id_number = id_number_ent.get())
        if verify_id_number:
            print("id is correct")
            verify_password = check_valid_password(id_number=id_number_ent.get(),password=password_ent.get())
            #if all the condition are correct then move to the dashboard student page
            if verify_password:
              id_number = id_number_ent.get()
              student_login_page_fm.destroy()
              student_dashboard(student_id=id_number)
              root.update()
            else:
                print("oop password is incorrect")
                password_ent.config(highlightbackground="red", highlightcolor='red')
                message_box(message="Incorrect Password ")

        else:
            print("!oop ID is incorrect")
            id_number_ent.config(highlightbackground="red", highlightcolor='red')
            message_box(message="Please Enter Valid ID")




    # creating a frame for student log in page seconde Phase
    student_login_page_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)
    # the header
    heading_lb = tk.Label(student_login_page_fm, text="Student Login Page", bg=bg_color, fg="white", font=("bold", 18))
    heading_lb.place(x=0, y=0, width=400)
    #creation of the back button
    back_btn = tk.Button(student_login_page_fm,text="←",font=("bold",20),fg=bg_color,bd=0,command=forward_to_welcome_page)
    back_btn.place(x=5,y=40)

    # inserting the icon
    stud_icon_lab = tk.Label(student_login_page_fm, image=login_student_icon)
    stud_icon_lab.place(x=150, y=40)
    # the lables and entry button
    id_number_lb = tk.Label(student_login_page_fm, text="Enter Student ID Number", font=("bold", 15), fg=bg_color)
    id_number_lb.place(x=80, y=140)
    id_number_ent = tk.Entry(student_login_page_fm, font=("bold", 15)
                             , justify=tk.CENTER, highlightcolor=bg_color, highlightbackground="gray",
                             highlightthickness=2)
    id_number_ent.bind('<KeyRelease>',lambda e:remove_highlight_warning(entry=id_number_ent))
    id_number_ent.place(x=80, y=190)
    # the lables and entry button
    password_lb = tk.Label(student_login_page_fm, text="Enter Student Password", font=("bold", 15), fg=bg_color)
    password_lb.place(x=80, y=240)
    password_ent = tk.Entry(student_login_page_fm, font=("bold", 15)
                            , justify=tk.CENTER, highlightcolor=bg_color, highlightbackground="gray",
                            highlightthickness=2, show="*")
    password_ent.place(x=80, y=290)
    password_ent.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=password_ent))
    show_hide_btn = tk.Button(student_login_page_fm, image=locked_icon, bd=0, command=show_hide_password)
    show_hide_btn.place(x=310, y=280)

    # login button
    loging_btn = tk.Button(student_login_page_fm, text="Login", font=("bold", 15), bg=bg_color, fg="white",command=login_account)
    loging_btn.place(x=95, y=340, width=200, height=40)
    # create the forget passsword
    forget_password_btn = tk.Button(student_login_page_fm, text="⚠️\nForget Password", fg=bg_color, bd=0,command=forget_page_password)
    forget_password_btn.place(x=150, y=390)
    student_login_page_fm.pack(pady=30)
    student_login_page_fm.pack_propagate(False)
    student_login_page_fm.configure(width=400, height=450)



#creation of the admin dashboard
def admin_dashboard():
    dashboard_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)
    options_fm = tk.Frame(dashboard_fm, highlightbackground=bg_color, highlightthickness=3, bg='gray')
    pages_fm = tk.Frame(dashboard_fm, bg="white")

    def switch(indicate,page):
        home_indicate.config(bg="gray")
        find_student_indicate.config(bg="gray")
        #anounce_indicate.config(bg="gray")

        indicate.config(bg=bg_color)

        for child in pages_fm.winfo_children():

            child.destroy()
            root.update()

        page()

    def logout():

        confirm = confirmation_box(message="Do You Want to\nLogout Your Account")

        if confirm:
            dashboard_fm.destroy()
            welcom_page()
            root.update()



    #home
    btn_home = tk.Button(options_fm, text="Home", font=("bold", 15),
                         fg=bg_color, bd=0, bg="gray", justify=tk.LEFT, command=lambda: switch(indicate=home_indicate,page=home_page) )
    btn_home.place(x=10, y=50)
    # indicate lable for home page button
    home_indicate = tk.Label(options_fm, text="", bg=bg_color)
    home_indicate.place(x=5, y=48, width=3, height=40)
    # find student
    btn_find_student = tk.Button(options_fm, text="Find\nStudent", font=("bold", 15),
                                 fg=bg_color, bd=0, bg="gray", justify=tk.LEFT,
                                 command=lambda: switch(indicate=find_student_indicate,page=find_student_page))
    btn_find_student.place(x=10, y=100)
    # find student indicate
    find_student_indicate = tk.Label(options_fm, text="", bg="gray")
    find_student_indicate.place(x=5, y=108, width=3, height=40)
    # announcement button
    #btn_anounce = tk.Button(options_fm, text="Announce\nment", font=("bold", 15),
                            # fg=bg_color, bd=0, bg="gray", justify=tk.LEFT,
                            # command=lambda: switch(indicate=anounce_indicate))
   # btn_anounce.place(x=10, y=170)
    # anounce indicate
    #anounce_indicate = tk.Label(options_fm, text="", bg="gray")
    #anounce_indicate.place(x=5, y=170, width=3, height=40)
    # logout button
    btn_logout = tk.Button(options_fm, text="Logout", font=("bold", 15),
                           fg=bg_color, bd=0, bg="gray",command=logout)
    btn_logout.place(x=10, y=170)


    options_fm.place(x=0, y=0, width=120, height=575)


    def home_page():
        home_page_fm = tk.Frame(pages_fm)
        admin_icon_lb = tk.Label(home_page_fm,image=login_admin_icon)
        admin_icon_lb.image = login_admin_icon
        admin_icon_lb.place(x=10,y=10)

        hi_lb = tk.Label(home_page_fm,text="!Hi Admin",font=('bold',15),)
        hi_lb.place(x=120, y=40)

        class_list_lb = tk.Label(home_page_fm,text="Number of Student By Class.",
                                 font=('bold',14),bg=bg_color,fg="white")
        class_list_lb.place(x=20,y=130)

        student_number_lb = tk.Label(home_page_fm,text='',font=('bold',13),justify=tk.LEFT)
        student_number_lb.place(x=20,y=170)

        for i in class_list:

            result = fetch_student_data(query=f"SELECT COUNT(*) FROM data WHERE student_class == '{i}' ")
            student_number_lb['text'] += f"{i} student_class: {result[0][0]}\n\n"

        home_page_fm.pack(fill=tk.BOTH, expand=True)
    def find_student_page():
        def find_student():
            found_data = ""

            if find_by_option_btn.get() == "id":
                found_data = fetch_student_data(query=f"""
                SELECT id_number,name,student_class,gender FROM data WHERE 
                id_number == '{search_input.get()}'
                                                    """)
            elif find_by_option_btn.get() == "name":
                found_data = fetch_student_data(query=f"""
                SELECT id_number,name,student_class,gender FROM data WHERE 
                name LIKE '%{search_input.get()}%'
                                                    """)
            elif find_by_option_btn.get() == "class":
                found_data = fetch_student_data(query=f"""
                SELECT id_number,name,student_class,gender FROM data WHERE 
                student_class == '{search_input.get()}'
                                                    """)
            elif find_by_option_btn.get() == "gender":
                found_data = fetch_student_data(query=f"""
                SELECT id_number,name,student_class,gender FROM data WHERE 
                gender == '{search_input.get()}'
                                      """)
                # for inserting the data in the treeview

            if found_data :
                for item in record_table.get_children():
                    record_table.delete((item))
                for details in found_data:
                    record_table.insert(parent='',index='end',values=details)
            else:
                for item in record_table.get_children():
                    record_table.delete(item)

        def generate_student_card():
            selection = record_table.selection()
            selected_id = record_table.item(item=selection,option='value')[0]

            get_student_details = fetch_student_data(f"""
               SELECT name,age,gender,student_class,phone_number,email FROM data WHERE id_number == '{selected_id}'

               """)
            get_student_pic = fetch_student_data(f"""
                   SELECT image FROM data WHERE id_number == '{selected_id}'

                   """)
            student_pic = BytesIO(get_student_pic[0][0])

            student_details = f"""
{selected_id}
{get_student_details[0][0]}
{get_student_details[0][2]}
{get_student_details[0][1]}
{get_student_details[0][3]}
{get_student_details[0][4]}
{get_student_details[0][5]}
                     """
            student_card_image_obj = draw_student_card(student_pic_path=student_pic, student_data=student_details)
            student_card_page(student_card_obj=student_card_image_obj,bypass_login_page=True)

        def clear_result():
            find_by_option_btn.set("id")

            search_input.delete(0,tk.END)

            for item in record_table.get_children():
                record_table.delete(item)
            generate_student_card_btn.config(state=tk.DISABLED)




        search_filters = ["id","name","class","gender"]

        find_student_fm = tk.Frame(pages_fm)
        find_student_record_lb = tk.Label(find_student_fm,text="Find Student Record",fg='white',
                                          font=("bold",14),bg=bg_color)
        find_student_record_lb.place(x=20, y=10,width=300)

        find_by_lb = tk.Label(find_student_fm,text="Find By",font=('bold',12))
        find_by_lb.place(x=15,y=50)


        find_by_option_btn = Combobox(find_student_fm,font=("Bold",13),state="readonly",values=search_filters)
        find_by_option_btn.place(x=80,y=50,width=100)
        find_by_option_btn.set("id")

        search_input = tk.Entry(find_student_fm,font=("bold",13))
        search_input.place(x=20,y=90)
        search_input.bind('<KeyRelease>',lambda e:find_student())

        record_table_lb = tk.Label(find_student_fm,text="Record Table",font=('Bold',13),bg=bg_color,fg="white")
        record_table_lb.place(x=20,y=160,width=300)

        #creation of the treeview for displaying data :first process
        record_table = Treeview(find_student_fm)
        record_table.place(x=0,y=200,width=350)
        record_table.bind('<<TreeviewSelect>>',lambda e:generate_student_card_btn.config(state=tk.NORMAL))

        #set the number of columns :second process
        record_table['columns'] = ("id","name","class","gender")
        record_table.column('#0',stretch=tk.NO,width=0)
        #using treeview heading we set the columns name
        #id :refereces to the column
        #text : ID number : what will display to the treeview
        #anchor:tk.west : the position

        record_table.heading("id",text="ID Number",anchor=tk.W)
        record_table.column("id",width=50,anchor=tk.W)

        record_table.heading("name", text="Name", anchor=tk.W)
        record_table.column("name", width=90, anchor=tk.W)

        record_table.heading("class", text=" Class", anchor=tk.W)
        record_table.column("class", width=40, anchor=tk.W)

        record_table.heading("gender", text="Gender", anchor=tk.W)
        record_table.column("gender", width=40, anchor=tk.W)


        generate_student_card_btn = tk.Button(find_student_fm,text="Generate Student card",
                                              font=('Bold',13),bg=bg_color,fg="white",state=tk.DISABLED,command=generate_student_card)
        generate_student_card_btn.place(x=160,y=450)

        clear_btn=tk.Button(find_student_fm,text="Clear",font=("bold",13),bg=bg_color,fg="white",command=clear_result)
        clear_btn.place(x=10,y=450)



        find_student_fm.pack(fill=tk.BOTH,expand=True)



    pages_fm.place(x=122,y=5,width=350,height=550)

    home_page()
    #find_student_page()


    dashboard_fm.pack(pady=5)
    dashboard_fm.pack_propagate(False)
    dashboard_fm.configure(width=480,height=580)

#Admin function page 3 pahse
def admin_login_page():
    #function to hide and show password
    def show_hide_passeword():

        if password_ent['show'] == "*":
                password_ent.config(show='')
                show_hide_btn.config(image=unlock_icon)
        else:
         password_ent.config(show='*')
         show_hide_btn.config(image=locked_icon)
    def forward_to_welcome_page():
        admin_login_page_fm.destroy()
        root.update()
        welcom_page()
    def login_account():
        if username_ent.get() == 'Admin':
            if password_ent.get() == 'admin':
                admin_login_page_fm.destroy()
                root.update()
                admin_dashboard()

            else:
                message_box(message="wrong Password")

        else:
            message_box(message="wrong Username")



    #creation of Admin account 3 phases
    admin_login_page_fm = tk.Frame(root,highlightbackground=bg_color, highlightthickness=3)
    #the header
    heading_lb = tk.Label(admin_login_page_fm, text="Admin Login Page", bg=bg_color, fg="white", font=("bold", 18))
    heading_lb.place(x=0, y=0, width=400)
    # creation of the back button
    back_btn = tk.Button(admin_login_page_fm, text="←", font=("bold", 20), fg=bg_color, bd=0,
                         command=forward_to_welcome_page)
    back_btn.place(x=5, y=40)
    # inserting the icon
    stud_icon_lab = tk.Label(admin_login_page_fm, image=login_admin_icon)
    stud_icon_lab.place(x=150, y=40)
    # the lables and entry button
    username_lb = tk.Label(admin_login_page_fm, text="Enter Admin User Name ", font=("bold", 15), fg=bg_color)
    username_lb.place(x=80, y=140)
    username_ent = tk.Entry(admin_login_page_fm, font=("bold", 15)
                                 , justify=tk.CENTER, highlightcolor=bg_color, highlightbackground="gray",
                                 highlightthickness=2)
    username_ent.place(x=80, y=190)
    # the lables and entry button
    password_lb = tk.Label(admin_login_page_fm, text="Enter Admin Password", font=("bold", 15), fg=bg_color)
    password_lb.place(x=80, y=240)
    password_ent = tk.Entry(admin_login_page_fm, font=("bold", 15)
                                , justify=tk.CENTER, highlightcolor=bg_color, highlightbackground="gray",
                                highlightthickness=2, show="*")
    password_ent.place(x=80, y=290)
    show_hide_btn = tk.Button(admin_login_page_fm, image=locked_icon, bd=0, command=show_hide_passeword)
    show_hide_btn.place(x=310, y=280)

    # login button
    loging_btn = tk.Button(admin_login_page_fm, text="Login", font=("bold", 15), bg=bg_color, fg="white",command=login_account)
    loging_btn.place(x=95, y=340, width=200, height=40)

    admin_login_page_fm.pack(pady=30)
    admin_login_page_fm.pack_propagate(False)
    admin_login_page_fm.configure(width=400, height=430)
student_gender = tk.StringVar()#for the radiobutton
 #student classes list
class_list = ["5th","6th","7th","8th","9th","9th","10th","11th","12th"]


# creating add account page 4 phase
def add_account_page():
    #load pic to create account
    pic_path = tk.StringVar()#the stringvar can save any type of variable
    pic_path.set('')#the picture will be save in the database
    def open_pic():
        path = askopenfilename()
        if path:
            img = ImageTk.PhotoImage(Image.open(path).resize((100,100)))
            #this pic_path willl help us to pictures to the database
            pic_path.set(path)

            add_pic_btn.config(image=img)
            add_pic_btn.image = img


    #creation of the frame

    def forward_to_welcome_page():
        ans = confirmation_box(message="Do You Want To Leave\nRegistration Form?")
        if ans:
            add_account_fm.destroy()
            root.update()
            welcom_page()
    def remove_highlight_warning(entry):
        if entry['highlightbackground'] != 'gray':
            if entry.get() != '':
                entry.config(highlightbackground="gray",highlightcolor=bg_color)

    def check_invalid_email(email):
        #using this pattern we will check email address format
        pattern = "^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$"
        match = re.match(pattern=pattern, string=email)
        return match
    def generate_id_number():
        generate_id = ''

        for t in range(6):

            generate_id += str(random.randint(0,9))
        student_id_en.config(state=tk.NORMAL)
        student_id_en.delete(0, tk.END)
        student_id_en.insert(tk.END, generate_id)
        student_id_en.config(state="readonly")



    def check_input_validation():
        if student_name_en.get() == '':
            student_name_en.config(highlightbackground="red",highlightcolor='red')
            student_name_en.focus()
            message_box(message='Student Full Name Is Required')
        elif student_age_en.get() == '':
            student_age_en.config(highlightbackground="red", highlightcolor='red')
            student_age_en.focus()
            message_box(message='Student Age Is Required')
        elif student_contact_en.get() == '':
            student_contact_en.config(highlightbackground="red", highlightcolor='red')
            student_contact_en.focus()
            message_box(message='Student Contact Is Required')
        elif student_class_btn.get() == '':
            student_class_btn.focus()
            message_box(message='Select Student Class Is Required')
        elif student_email_en.get() == '':
            student_email_en.config(highlightbackground="red", highlightcolor='red')
            student_email_en.focus()
            message_box(message='Student Email Is Required')
        elif not check_invalid_email(email=student_email_en.get().lower()):
            student_email_en.config(highlightcolor="red", highlightbackground='red')
            student_email_en.focus()
            message_box(message="Please Enter a Valid\nEmail Address")

        elif student_password_en.get() == '':
            student_password_en.config(highlightbackground="red", highlightcolor='red')
            student_password_en.focus()
            message_box(message='Create a  Password Is Required')
        else:
            image = b''
            if pic_path.get() != '':
                resize_pic = Image.open(pic_path.get()).resize((100,100))
                resize_pic.save('temp_pic.png')

                read_data = open('temp_pic.png','rb')
                image = read_data.read()
                read_data.close()
            else:
                read_data = open('images/add_image.png', 'rb')
                image = read_data.read()
                read_data.close()
                pic_path.set('images/add_image.png')


            add_data(id_number=student_id_en.get(),password=student_password_en.get(),
                     name=student_name_en.get(),age=student_age_en.get(),
                     gender=student_gender.get(),phone_number=student_contact_en.get(),
                     student_class=student_class_btn.get(),email=student_email_en.get(),
                     image= image )

            data = f"""
            {student_id_en.get()}
            {student_name_en.get()}
             {student_gender.get()}
            {student_age_en.get()}
            {student_class_btn.get()}
            {student_contact_en.get()}
            {student_email_en.get()}
            """
            get_student_card = draw_student_card(student_pic_path=pic_path.get(),student_data= data)
            student_card_page(student_card_obj=get_student_card )
            add_account_fm.destroy()
            message_box('Account Successful Created')


    add_account_fm = tk.Frame(root,highlightbackground=bg_color, highlightthickness=3)
    #creating a frame for a pic
    add_pic_fm  = tk.Frame(add_account_fm,highlightbackground=bg_color, highlightthickness=2)
    add_pic_btn = tk.Button(add_pic_fm,image=add_student_pic,
                            bd=0,command=open_pic)
    add_pic_btn.pack()
    add_pic_fm.place(x=5,y=5,width=105,height=105)
    student_name_lb = tk.Label(add_account_fm,text="Enter Student Full Name",font=("bold",12))
    student_name_lb.place(x=5,y=130)
    student_name_en = tk.Entry(add_account_fm,font=("bold",15)
                               ,highlightbackground="gray", highlightthickness=2,highlightcolor=bg_color)
    student_name_en.place(x=5,y=160,width=180)
    #creating a bind to mage the color afet and before entering the data
    student_name_en.bind('<KeyRelease>',lambda e:remove_highlight_warning(entry=student_name_en))
    #creation of the radiobutton for gender
    student_gender_lb = tk.Label(add_account_fm,text="Select Student Gender.",font=("bold",12))
    student_gender_lb.place(x=5,y=210)
    male_gender_btn = tk.Radiobutton(add_account_fm,text="Male",font=("bold",12),variable=student_gender,value='male')
    male_gender_btn.place(x=5,y=235)
    female_gender_btn = tk.Radiobutton(add_account_fm,text="Female",font=("bold",12),variable=student_gender,value='female')
    female_gender_btn.place(x=75,y=235)
    #we set male by default
    student_gender.set('male')
    #enter the age
    student_age_lb = tk.Label(add_account_fm,text="Enter Student Age",font=("bold",12))
    student_age_lb.place(x=5,y=275)
    student_age_en = tk.Entry(add_account_fm,font=("bold",15)
                               ,highlightbackground="gray", highlightthickness=2,highlightcolor=bg_color)
    student_age_en.place(x=5,y=305,width=180)
    student_age_en.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_age_en))

    student_contact_lb = tk.Label(add_account_fm,text="Enter Contact Phone Number",font=("bold",12))
    student_contact_lb.place(x=5,y=350)
    student_contact_en = tk.Entry(add_account_fm,font=("bold",15)
                               ,highlightbackground="gray", highlightthickness=2,highlightcolor=bg_color)
    student_contact_en.place(x=5,y=390,width=180)
    student_contact_en.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_contact_en))

    select_student_lb = tk.Label(add_account_fm,text="Select Student Class ",font=("bold",12))
    select_student_lb.place(x=5,y=445)
    student_class_btn = ttk.Combobox(add_account_fm,font = ("bold",15),state='readonly',values=class_list)
    student_class_btn.place(x=5,y=475,width=180,height=30)
    student_class_btn.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_class_btn))
    #student id section
    student_id_lb = tk.Label(add_account_fm,text="Student ID Number:",font=("bold",12))
    student_id_lb.place(x=240,y=35)
    student_id_en = tk.Entry(add_account_fm,font=("bold",12),bd=0)
    student_id_en.place(x=380,y=35,width=80)
    student_id_en.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_id_en))



    student_id_en.config(state='readonly')

    generate_id_number()


    id_info_lb = tk.Label(add_account_fm,text=""" Automatically Generated ID Number
!Remenber Using This ID Number
Student Will Login Account""",justify=tk.LEFT)
    id_info_lb.place(x=240,y=65)
    student_email_lb = tk.Label(add_account_fm,text="Enter Student Email Address",font=("bold",12))
    student_email_lb.place(x=240,y=130)
    student_email_en = tk.Entry(add_account_fm,font=("Bold",15)
                               ,highlightbackground="gray", highlightthickness=2,highlightcolor=bg_color)
    student_email_en.place(x=240,y=160,width=200)
    email_info_lb = tk.Label(add_account_fm,text=""" Via Email Address Student 
Can Recover Account
!In case Forgetting Password and Also 
Student will get Future Notification""",justify=tk.LEFT)
    email_info_lb.place(x=240,y=200)
    student_email_en.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_email_en))
    student_password_lb = tk.Label(add_account_fm,text="Create Account Password",font=("bold",12))
    student_password_lb.place(x=240,y=275)
    student_password_en = tk.Entry(add_account_fm,font=("bold",15)
                               ,highlightbackground="gray", highlightthickness=2,highlightcolor=bg_color)
    student_password_en.place(x=240,y=307,width=180)
    password_info_lb = tk.Label(add_account_fm,text=""" Via Student Created Password
 and Provided Student ID Number
 Student Can Login Account""",justify=tk.LEFT)
    password_info_lb.place(x=240,y=345)
    student_password_en.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_password_en))
    #submit Button
    home_btn = tk.Button(add_account_fm,text="Home",font=("Bold",15),bg="red",fg="white",bd=0,command=forward_to_welcome_page)
    home_btn.place(x=240,y=420)
    #submit button
    submit_btn = tk.Button(add_account_fm,text="Submit",font=("Bold",15),bg=bg_color,fg="white",bd=0,command=check_input_validation)
    submit_btn.place(x=360,y=420)

    add_account_fm.pack(pady=30)
    add_account_fm.pack_propagate(False)
    add_account_fm.configure(width=480, height=580)


init_database()
#admin_dashboard()
welcom_page()
#admin_login_page()


root.mainloop()