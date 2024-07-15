
#https://towardsdatascience.com/3-ways-to-convert-python-app-into-apk-77f4c9cd55af
import clipboard

import datetime
import sqlite3
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner

from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
Window.size = (300, 600)

text_report=None
pahina_no = 1
miembro_rows = []
linya_max = 10
mga_miembro = []
filter_text_row=None
button_prev=None
button_next=None
pager_row=None
text_search_name=None
text_search_group=None
sm=None

class InputBatchPop(Popup):
    def __init__(self, memberRow,batch_button, **kwargs):
        super(InputBatchPop, self).__init__(**kwargs)
        self.auto_dismiss=False
        self.size_hint=(1,0.7)
        self.pos_hint={"x":0.0,"top":0.9}
        self.add_widget(ChangeBatchLayout(memberRow,batch_button))

class ChangeBatchLayout(BoxLayout):
    def __init__(self, memberRow,batch_button,**kwargs):
        super(ChangeBatchLayout, self).__init__(**kwargs)
        self.memberRow=memberRow
        self.orientation='vertical'
        self.batch_button=batch_button
        self.days=0
        self.hours=0
        self.minutes=0

        if self.memberRow!=None:
            if self.memberRow.member.datum[10]!=None:
                minutes=int(self.memberRow.member.datum[10])
                self.days=int(minutes/1440)
                minutes=minutes-(self.days*1440)
                self.hours=int(minutes/60)
                minutes=minutes-(self.hours*60)
                self.minutes=minutes
        else:
            if MainApp.batch_mins!=None:
                minutes=int(MainApp.batch_mins)
                self.days=int(minutes/1440)
                minutes=minutes-(self.days*1440)
                self.hours=int(minutes/60)
                minutes=minutes-(self.hours*60)
                self.minutes=minutes

        def callback_change_batch_cancel(instance):
            MainApp.inputBatchPop.dismiss()


        def callback_change_batch_save(instance):
            global miembro_rows
            if self.memberRow!=None:
                y = list(self.memberRow.member.datum)
                self.hours=int(self.batchTimeLayout.hour_spinner.text)
                self.minutes=int(self.batchTimeLayout.minute_spinner.text)

                y[10]=(self.days*24*60)+(self.hours*60)+self.minutes
                
                self.memberRow.member.datum = tuple(y)
                miembro_rows[self.memberRow.numero].member=self.memberRow.member
                MainApp.data[self.memberRow.member.bilang]=tuple(y)
                self.memberRow.refresh_me()
            else:
                self.hours=int(self.batchTimeLayout.hour_spinner.text)
                self.minutes=int(self.batchTimeLayout.minute_spinner.text)

                MainApp.batch_mins=(self.days*24*60)+(self.hours*60)+self.minutes
                sql = 'UPDATE events SET batch_mins=? WHERE event_date = ?'
                result=MainApp.cur.execute(sql, (MainApp.batch_mins,str(MainApp.event_date)[0:10]))
                MainApp.con.commit()
                self.batch_button.text= batch_display_in_button(MainApp.batch_mins)                

            MainApp.inputBatchPop.dismiss()

        self.weekDaysLayout=WeekDaysLayout(change_batch_layout=self,size_hint=(1, .2))
        self.add_widget(self.weekDaysLayout)

        self.batchTimeLayout=BatchTimeLayout(change_batch_layout=self,size_hint=(1, .4))
        self.add_widget(self.batchTimeLayout)


        save_button = Button(text="Save",size_hint=(1, .3))
        save_button.bind(on_press=callback_change_batch_save)
        self.add_widget(save_button)

        cancel_button = Button(text="Cancel",size_hint=(1, .3))
        cancel_button.bind(on_press=callback_change_batch_cancel)
        self.add_widget(cancel_button)


class BatchTimeLayout(StackLayout):
    def __init__(self, change_batch_layout,**kwargs):
        super(BatchTimeLayout, self).__init__(**kwargs)
        self.change_batch_layout=change_batch_layout

        # self.orientation='horizontal'

        # <MyDropDown@DropDown>:
        #     max_height: 100
        # dropdown_cls='MyDropDown',
        # from kivy.factory import Factory
        #                             option_cls=Factory.get("MySpinnerOption"),
        # <MySpinnerOption@SpinnerOption>:
        #     height:44        

        self.hour_spinner=Spinner(text="04",
                            values=["04","06","08","12","15","17","18"],
                            size_hint=(.5,.5),
                            pos_hint={'center_x':0.5,'center_y':0.5}  
        )

        self.minute_spinner=Spinner(text="00",
                            values=["00","30"],
                            size_hint=(.5,.5),
                            pos_hint={'center_x':0.5,'center_y':0.5}  
        )


        chour= str(self.change_batch_layout.hours).rjust(2,'0')
        self.hour_spinner.text=chour
        cminute= str(self.change_batch_layout.minutes).rjust(2,'0')
        self.minute_spinner.text=cminute


        self.add_widget(self.hour_spinner)
        self.add_widget(self.minute_spinner)

        def callback_hour_minus(instance):
            if self.hour_spinner.text=="00":
                return
            hour=int(self.hour_spinner.text)
            hour-=1
            self.hour_spinner.text=str(hour).rjust(2,'0')
            
        def callback_hour_plus(instance):
            hour=int(self.hour_spinner.text)
            hour+=1
            if hour==24:
                hour==0
            self.hour_spinner.text=str(hour).rjust(2,'0')

        def callback_minute_minus(instance):
            if self.minute_spinner.text=="00":
                return
            minute=int(self.minute_spinner.text)
            minute-=1
            self.minute_spinner.text=str(minute).rjust(2,'0')            

        def callback_minute_plus(instance):
            minute=int(self.minute_spinner.text)
            minute+=1
            if minute==60:
                minute==0
            self.minute_spinner.text=str(minute).rjust(2,'0')


        btn_hour_minus = Button(text="-",size_hint=(.25,.5))
        btn_hour_minus.bind(on_press=callback_hour_minus)
        self.add_widget(btn_hour_minus)
        btn_hour_plus = Button(text="+",size_hint=(.25,.5))
        btn_hour_plus.bind(on_press=callback_hour_plus)
        self.add_widget(btn_hour_plus)

        btn_minute_minus = Button(text="-",size_hint=(.25,.5))
        btn_minute_minus.bind(on_press=callback_minute_minus)
        self.add_widget(btn_minute_minus)
        btn_minute_plus = Button(text="+",size_hint=(.25,.5))
        btn_minute_plus.bind(on_press=callback_minute_plus)
        self.add_widget(btn_minute_plus)


class DayButton(ToggleButton):
    def __init__(self, change_batch_layout,button_no,week_no,**kwargs):
        super(DayButton, self).__init__(**kwargs)

        if week_no>6:
            week_no=week_no-7

        self.week_no=week_no
        self.button_no=button_no

        self.text=weekName(week_no)
        if button_no==change_batch_layout.days:
            self.state="down"

        def callback_push_day():
            for d in MainApp.day_button:
                if d.button_no==self.button_no:
                    d.state="down"
                    change_batch_layout.days=(d.button_no)
                    print(change_batch_layout.days)
                else:
                    d.state="normal"


        self.on_press=callback_push_day




class WeekDaysLayout(BoxLayout):
    def __init__(self, change_batch_layout,**kwargs):
        super(WeekDaysLayout, self).__init__(**kwargs)
        self.orientation='horizontal'
        week_no=MainApp.event_date.weekday()


        MainApp.day_button = [DayButton(change_batch_layout,0,week_no,size_hint=(1, 1)),
                            DayButton(change_batch_layout,1,week_no+1,size_hint=(1, 1)),
                            DayButton(change_batch_layout,2,week_no+2,size_hint=(1, 1)),
                            DayButton(change_batch_layout,3,week_no+3,size_hint=(1, 1)),
                            DayButton(change_batch_layout,4,week_no+4,size_hint=(1, 1)),
                            DayButton(change_batch_layout,5,week_no+5,size_hint=(1, 1)),
                            DayButton(change_batch_layout,6,week_no+6,size_hint=(1, 1)),
        ]

        

        self.add_widget(MainApp.day_button[0])
        self.add_widget(MainApp.day_button[1])
        self.add_widget(MainApp.day_button[2])
        self.add_widget(MainApp.day_button[3])
        self.add_widget(MainApp.day_button[4])
        self.add_widget(MainApp.day_button[5])
        self.add_widget(MainApp.day_button[6])
    
def weekDay(date: datetime):
    week_no=date.weekday()
    return weekName(week_no)


def weekName(week_no):
    if week_no == 0:
        return "Mon"
    elif week_no == 1:
        return "Tue"
    elif week_no == 2:
        return "Wed"
    elif week_no == 3:
        return "Thu"
    elif week_no == 4:
        return "Fri"
    elif week_no == 5:
        return "Sat"
    elif week_no == 6:
        return "Sun"
    else:
        return "   "


class FilterTextRow(BoxLayout):
    def __init__(self, **kwargs):
        global text_search_name
        global text_search_group

        super(FilterTextRow, self).__init__(**kwargs)

        text_search_name = TextInput()
        text_search_group = TextInput(size_hint=(.2, 1))
        self.add_widget(text_search_name)
        self.add_widget(text_search_group)

class EventDateButtonRow(BoxLayout):
    def __init__(self, **kwargs):
        super(EventDateButtonRow, self).__init__(**kwargs)

        def callback_report(instance):
            global sm
            sm.current = "event_screen"

        def callback_change_batch(instance):
            MainApp.inputBatchPop=InputBatchPop(memberRow=None,batch_button=self.batch_button)
            MainApp.inputBatchPop.title=""
            MainApp.inputBatchPop.open()


        MainApp.btn_event_date = Button(text=weekDay(MainApp.event_date)+" "+str(MainApp.event_date)[0:10],size_hint=(1, 1))
        MainApp.btn_event_date.bind(on_press=callback_report)
        self.add_widget(MainApp.btn_event_date)


        self.batch_button = Button(text="",size_hint=(.295, 1),font_size='11sp')
        self.batch_button.text= batch_display_in_button(MainApp.batch_mins)
        self.batch_button.bind(on_press=callback_change_batch)
        self.add_widget(self.batch_button)        

class FilterButtonRow(BoxLayout):
    def __init__(self, **kwargs):
        super(FilterButtonRow, self).__init__(**kwargs)

        def callback_filter_all(instance):
            MainApp.filter_now("all")

        def callback_filter_wo(instance):
            MainApp.filter_now("wo")

        def callback_report(instance):
            global sm
            sm.current = "report_screen"

        btn_report = Button(text="Report",size_hint=(.5, 1))
        btn_report.bind(on_press=callback_report)
        self.add_widget(btn_report)

        btn_filter_all = Button(text="Filter w/ selected")
        btn_filter_all.bind(on_press=callback_filter_all)
        self.add_widget(btn_filter_all)

        btn_filter_wo = Button(text="Filter",size_hint=(.5, 1))
        btn_filter_wo.bind(on_press=callback_filter_wo)
        self.add_widget(btn_filter_wo)

def a_type_display(a_type):
    if a_type==None:
        return '(Lokal)'
    elif a_type=="y":
        return '(yt)'
    elif a_type=="z":
        return '(Zoom)'
    elif a_type=="C":
        return '(Chapel)'
    elif a_type=="O":
        return '(Other-lokal)'
    return ''


def batch_display(batch_mins):
    if batch_mins==None:
        return ''
    time_change = datetime.timedelta(minutes=batch_mins) 
    new_time = MainApp.event_date + time_change 
    
    batch_str=weekDay(new_time)+" "+str(new_time.strftime("%I%M%p"))

    return batch_str

def batch_display_in_button(batch_mins):
    batch_str=batch_display(batch_mins)
    batch_str=batch_str[0:8]+batch_str[8:9]
    return batch_str

class MemberRow(BoxLayout):
    def __init__(self, member,numero,**kwargs):
        super(MemberRow, self).__init__(**kwargs)

        def callback_change_a_type(instance):
            global miembro_rows
            y = list(self.member.datum)
            if y[5]!=None:
                if y[8]==None:
                    y[8]="z"
                elif y[8]=='z':
                    y[8]="y"
                elif y[8]=='y':
                    y[8]="O"
                elif y[8]=='O':
                    y[8]="C"
                else:
                    y[8]=None
            self.member.datum = tuple(y)
            miembro_rows[self.numero].member=self.member
            MainApp.data[self.member.bilang]=tuple(y)
            self.refresh_me()
            
        def callback_change_batch(instance):
            MainApp.inputBatchPop=InputBatchPop(memberRow=self,batch_button=None)
            MainApp.inputBatchPop.title=self.member.datum[1]+" "+self.member.datum[2]
            MainApp.inputBatchPop.open()

        def callback_toggle(instance):
            global miembro_rows
            y = list(self.member.datum)
            if y[5]==None:
                y[5]="1"
            else:
                y[5]=None

            if y[10]==None and y[5]!=None:
                y[10]=MainApp.batch_mins


            self.member.datum = tuple(y)
            miembro_rows[self.numero].member=self.member
            MainApp.data[self.member.bilang]=tuple(y)
            self.refresh_me()

        self.numero=numero
        self.member=member
        self.toggle=ToggleButton(size_hint=(.2, 1))
        self.toggle.bind(on_press=callback_toggle)

        self.add_widget(self.toggle)

        self.label = Button(text="", size_hint=(1.0, 1.0), halign="left", valign="middle",padding=[10,0])
        self.label.bind(size=self.label.setter('text_size'))    

        self.group_button = Button(text="",size_hint=(.25, 1))
        self.add_widget(self.label)
        self.add_widget(self.group_button)

        self.a_type_button = Button(text="",size_hint=(.25, 1))
        self.a_type_button.bind(on_press=callback_change_a_type)
        self.add_widget(self.a_type_button)

        self.batch_button = Button(text="",size_hint=(.50, 1),font_size='11sp')
        self.batch_button.bind(on_press=callback_change_batch)
        self.add_widget(self.batch_button)


        self.refresh_me()



    def refresh_me(self):
        if hasattr(self.member, 'datum'):

            self.label.text=self.member.datum[1]+" "+self.member.datum[2]
            self.group_button.text=self.member.datum[3]
            if self.member.datum[5]==None:
                self.toggle.state="normal"
            else:
                self.toggle.state="down"

            self.a_type_button.text=""
            if self.member.datum[5]!=None:
                if self.member.datum[8]==None:
                    self.a_type_button.text="L"
                elif self.member.datum[8]=="y":
                    self.a_type_button.text="yt"
                elif self.member.datum[8]=="z":
                    self.a_type_button.text="z"
                elif self.member.datum[8]=="O":
                    self.a_type_button.text="oL"
                elif self.member.datum[8]=="C":
                    self.a_type_button.text="C"

            self.batch_button.text= batch_display_in_button(self.member.datum[10])


class PagerRow(BoxLayout):

    def act_paging(self):
        global pahina_no
        global miembro_rows
        global linya_max
        global mga_miembro
        global button_prev
        global button_next

        for i,row in enumerate(miembro_rows):
            element=i+((pahina_no*linya_max)-linya_max)
            if element<len(mga_miembro):
                # mga_miembro.append(MainAppMember(datum,bilang))
                row.member=mga_miembro[element]
            else:
                row.member=MainAppMember((0,"","","","",None,None,None,None,None,None,None,None),0)
            row.refresh_me()

        button_prev.text=str((pahina_no*linya_max)-linya_max)
        button_next.text=str(len(mga_miembro)-(pahina_no*linya_max))        


    def __init__(self, **kwargs):
        global button_prev
        global button_next
        global miembro_rows

        super(PagerRow, self).__init__(**kwargs)
        linya_max=len(miembro_rows)

        def callback_next(instance):
            global pahina_no
            element=0+(((pahina_no+1)*linya_max)-linya_max)
            if element>=len(mga_miembro):
                return
            pahina_no=pahina_no+1

            PagerRow.act_paging(self)


        def callback_prev(instance):
            global pahina_no
            if pahina_no>1:
                pahina_no=pahina_no-1
            else:
                pahina_no=1
            PagerRow.act_paging(self)


        button_prev = Button(text=str(0))
        button_prev.bind(on_press=callback_prev)

        button_next = Button(text=str(len(mga_miembro)-(pahina_no*linya_max)))
        button_next.bind(on_press=callback_next)

        self.add_widget(button_prev)
        self.add_widget(button_next)


class MainGrid(GridLayout):
    def __init__(self, **kwargs):
        global pahina_no
        global miembro_rows
        super(MainGrid, self).__init__(**kwargs)
        pahina_no=1
        self.cols = 1
        miembro_rows=[]

        self.add_widget(EventDateButtonRow())
        for i in range(linya_max):
            if len(mga_miembro)>=1:
                miembro_rows.append(MemberRow(mga_miembro[i],i))
            else:
                miembro_rows.append(MemberRow((),i))    
            self.add_widget(miembro_rows[i])

        filter_text_row=FilterTextRow()
        pager_row=PagerRow()
        self.add_widget(pager_row)
        self.add_widget(filter_text_row)
        self.add_widget(FilterButtonRow())



class ReportGrid(BoxLayout):

    def __init__(self, **kwargs):
        global text_report
        super(ReportGrid, self).__init__(**kwargs)
        self.orientation='vertical'

        text_report = TextInput(text="")
        self.add_widget(text_report)
        def callback_main(instance):
            global sm
            sm.current = "main_screen"

        btn_main = Button(text="Go back to main",size_hint=(1,.1))
        btn_main.bind(on_press=callback_main)
        self.add_widget(btn_main)

def validate_date(date_text):
    try:
        datetime.date.fromisoformat(date_text)
    except ValueError:
        return False
    
    return True

class EventDateInputTextLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(EventDateInputTextLayout, self).__init__(**kwargs)
        self.orientation='horizontal'
        
        MainApp.text_year = TextInput(text="",size_hint=(1,.70),pos_hint={'x': 0, 'center_y': .5})
        self.add_widget(Label(text="Y:",size_hint=(.3,.70),pos_hint={'x': 0, 'center_y': .5}))
        self.add_widget(MainApp.text_year)

        MainApp.text_month = TextInput(text="",size_hint=(.5,.70),pos_hint={'x': 0, 'center_y': .5})
        self.add_widget(Label(text="M:",size_hint=(.3,.70),pos_hint={'x': 0, 'center_y': .5}))
        self.add_widget(MainApp.text_month)

        MainApp.text_day = TextInput(text="",size_hint=(.5,.70),pos_hint={'x': 0, 'center_y': .5})
        self.add_widget(Label(text="D:",size_hint=(.3,.70),pos_hint={'x': 0, 'center_y': .5}))
        self.add_widget(MainApp.text_day)

        def callback_look(instance):
            test_event_date=str(MainApp.text_year.text).strip()+'-'+str(MainApp.text_month.text).rjust(2,'0')+'-'+str(MainApp.text_day.text).rjust(2,'0')
            
            if not validate_date(test_event_date):
                MainApp.eventCodeInputLayout.event_code_spinner.disabled=True
                MainApp.eventTitleInputTextLayout.text_title.text = 'Invalid date'
                return
            MainApp.eventCodeInputLayout.event_code_spinner.disabled=False

            #                        0          1           2         3           
            query = "SELECT event_date,event_code,event_title,foot_note FROM events WHERE event_date=?"
            MainApp.cur.execute(query,(test_event_date,))
            events_record = MainApp.cur.fetchone()

            MainApp.eventCodeInputLayout.event_code_spinner.text = ''
            MainApp.eventTitleInputTextLayout.text_title.text = ''
            MainApp.eventFootnoteInputTextLayout.text_foot.text = ''

            if events_record!=None:
                if events_record[1]!=None:
                    MainApp.eventCodeInputLayout.event_code_spinner.text = str(events_record[1])

                if events_record[2]!=None:
                    MainApp.eventTitleInputTextLayout.text_title.text = str(events_record[2])

                if events_record[3]!=None:
                    MainApp.eventFootnoteInputTextLayout.text_foot.text = str(events_record[3])

        self.add_widget(Label(text=" ",size_hint=(.1,.70),pos_hint={'x': 0, 'center_y': .5}))
        btn_main = Button(text="look",size_hint=(.9,.70),pos_hint={'x': 0, 'center_y': .5})
        btn_main.bind(on_press=callback_look)
        self.add_widget(btn_main)



class EventTitleInputTextLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(EventTitleInputTextLayout, self).__init__(**kwargs)
        self.orientation='vertical'
        
        self.text_title = TextInput(text="",size_hint=(1,.95),pos_hint={'x': 0, 'center_y': .5})
        self.add_widget(Label(text="Title:",size_hint=(1,.2),pos_hint={'x': 0, 'center_y': .5}))
        self.add_widget(self.text_title)

class EventCodeInputLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(EventCodeInputLayout, self).__init__(**kwargs)
        self.event_code_spinner=Spinner(text="",
                            values=["","TG","WS","PM","PM/WS","TG1","TG2","TG3"],
                            size_hint=(.5,.5),
                            pos_hint={'center_x':0.5,'center_y':0.5}  
        )

        self.add_widget(self.event_code_spinner)


class EventFootnoteInputTextLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(EventFootnoteInputTextLayout, self).__init__(**kwargs)
        self.orientation='vertical'
        
        self.text_foot = TextInput(text="",size_hint=(1,.95),pos_hint={'x': 0, 'center_y': .5})
        self.add_widget(Label(text="Footnote:",size_hint=(1,.1),pos_hint={'x': 0, 'center_y': .5}))
        self.add_widget(self.text_foot)



class EventDateGrid(BoxLayout):

    def __init__(self, **kwargs):
        
        super(EventDateGrid, self).__init__(**kwargs)
        self.orientation='vertical'
    
        

        eventDateInputTextLayout=EventDateInputTextLayout(size_hint=(.98,.2))
        self.add_widget(eventDateInputTextLayout)

        MainApp.eventCodeInputLayout=EventCodeInputLayout(size_hint=(.80,.3),pos_hint={'x': 0, 'center_x': .5})
        self.add_widget(MainApp.eventCodeInputLayout)

        MainApp.eventTitleInputTextLayout=EventTitleInputTextLayout(size_hint=(.98,.3))
        self.add_widget(MainApp.eventTitleInputTextLayout)

        MainApp.eventFootnoteInputTextLayout=EventFootnoteInputTextLayout(size_hint=(.98,.9))
        self.add_widget(MainApp.eventFootnoteInputTextLayout)




        def callback_save_event(instance):
            global mga_miembro
            global pahina_no
            global miembro_rows
            global pager_row
            test_event_date=str(MainApp.text_year.text).strip()+'-'+str(MainApp.text_month.text).rjust(2,'0')+'-'+str(MainApp.text_day.text).rjust(2,'0')

            event_code = MainApp.eventCodeInputLayout.event_code_spinner.text
            event_title= MainApp.eventTitleInputTextLayout.text_title.text
            foot_note  = MainApp.eventFootnoteInputTextLayout.text_foot.text

            #                        0          1           2         3      
            query = "SELECT event_date,event_code,event_title,foot_note FROM events WHERE event_date=?"
            MainApp.cur.execute(query,(test_event_date,))
            events_record = MainApp.cur.fetchone()

            # print(data_one)
            if events_record!=None:
                sql = 'UPDATE events SET event_code=?,event_title=?,foot_note=? WHERE event_date = ?'
                MainApp.cur.execute(sql, (event_code,event_title,foot_note,test_event_date))
                MainApp.con.commit()
            else:
                sql = 'INSERT INTO events VALUES(?,?,?,?,?)'
                MainApp.cur.execute(sql, (test_event_date,event_code,event_title,foot_note,None))
                MainApp.con.commit()


            sql = 'UPDATE setup SET event_date=?'
            MainApp.cur.execute(sql, (test_event_date,))
            MainApp.con.commit()

            MainApp.event_date,MainApp.batch_mins,MainApp.event_title,MainApp.foot_note = make_setup(MainApp.cur)
            query = "SELECT members.key_id,first_name,last_code,group_code,member_type,checked,checked,event_date,a_type,a_type,batch_mins,batch_mins,sex FROM members LEFT OUTER JOIN attendance ON members.key_id=attendance.key_id AND attendance.event_date=? ORDER BY substr('0000000000' || group_code, -10, 10),first_name"
            MainApp.cur.execute(query,(str(MainApp.event_date)[0:10],))
            MainApp.data = MainApp.cur.fetchall()

            pahina_no = 1
            # miembro_rows = []
            mga_miembro = []           
            for bilang,datum in enumerate(MainApp.data):
                mga_miembro.append(MainAppMember(datum,bilang)) 
            PagerRow.act_paging(pager_row)



            MainApp.btn_event_date.text=weekDay(MainApp.event_date)+" "+str(MainApp.event_date)[0:10]
            print(MainApp.btn_event_date.text)
            global sm
            sm.current = "main_screen"            

        btn_save_event = Button(text="Save the event",size_hint=(.80,.3),pos_hint={'x': 0, 'center_x': .5})
        btn_save_event.bind(on_press=callback_save_event)
        self.add_widget(btn_save_event)

        self.add_widget(Label(text="",size_hint=(.98,.3)))

        def callback_main(instance):
            global sm
            sm.current = "main_screen"

        btn_main = Button(text="Go back to main",size_hint=(1,.2))
        btn_main.bind(on_press=callback_main)
        self.add_widget(btn_main)



class MyMainWindow(ScreenManager):
    def __init__(self, **kwargs):
        global sm
        super(MyMainWindow, self).__init__(**kwargs)
        sm = self
        self.add_widget(MyMainScreen(name='main_screen'))
        self.add_widget(MyReportScreen(name='report_screen'))
        self.add_widget(MyEventDateScreen(name='event_screen'))
        # self.add_widget(MyMainPage())
        # self.add_widget(MyReportPage())


class MyMainPage(GridLayout):
    def __init__(self, **kwargs):
        super(MyMainPage, self).__init__(**kwargs)
        self.cols=1
        self.rows=1
        self.add_widget(MainGrid())

class MyMainScreen(Screen):
    pass
    # def __init__(self, **kwargs):
    #     self.add_widget(MyMainPage())


class MyReportPage(GridLayout):
    def __init__(self, **kwargs):
        super(MyReportPage, self).__init__(**kwargs)
        self.cols=1
        self.rows=1
        self.add_widget(ReportGrid())

class MyEventDatePage(GridLayout):
    def __init__(self, **kwargs):
        super(MyEventDatePage, self).__init__(**kwargs)
        self.cols=1
        self.rows=1
        self.add_widget(EventDateGrid())


class MyEventDateScreen(Screen):
        
    def on_leave(self, *args):
        return super().on_leave(*args)

    def on_enter(self, *args):
        (year,month,day)=my_string_2_date(str(MainApp.event_date))
        MainApp.text_year.text=str(year)
        MainApp.text_month.text=str(month)
        MainApp.text_day.text=str(day)


        return super().on_enter(*args)


class MyReportScreen(Screen):
    def report_per_group(self):
        i=0
        j=0
        if MainApp.event_title!=None:
            report_text=MainApp.event_title
        else:
            report_text='<no title yet>'

        report_text=report_text+"\n"+MainApp.event_date.strftime("%B %d, %Y")
        report_text=report_text+"\nGroup "+self.search_group

        lines=[]

        for bilang,datum in enumerate(MainApp.data):
            name=datum[1]+" "+datum[2][0:1]+"."
            group=datum[3].upper().strip()
            checked=datum[5]
            
            if self.search_group==group:
                if checked!=None:
                    a_type=a_type_display(datum[8])
                    bs=""
                    if datum[12]!=None:
                        if datum[12]==1:
                            bs="Bro "
                        else:
                            bs="Sis "
                    # report_text=report_text+"\n"+str(i)+" "+bs+name+a_type
                    lines.append((datum[10],bs+name+a_type))
                else:
                    j+=1

            if datum[5]!=datum[6] or datum[8]!=datum[9] or datum[10]!=datum[11]:
                MainApp.save_now(datum)
                y = list(datum)
                y[6]=y[5]
                y[9]=y[8]
                y[11]=y[10]
                MainApp.data[bilang]=tuple(y)

        lines.sort(key=lambda x: x[0])          
        bm_current=0
        for bm,name in lines:
            i+=1
            if bm!=None and bm!=bm_current:
                report_text=report_text+"\n\n"+batch_display(bm)
                bm_current=bm
               
            report_text=report_text+"\n"+str(i)+" "+name
        
        for i in range(i,i+j):
            report_text=report_text+"\n"+str(i+1)
    
        report_text=report_text+'\n\n'+MainApp.foot_note
        return report_text
    

    def report_total_all(self):
        number_total=0
        number_local=0
        number_zoom=0
        number_yt=0
        number_ol=0
        number_c=0

        for bilang,datum in enumerate(MainApp.data):
            if datum[5]!=None:
                if datum[8]=="z":
                    number_zoom+=1
                elif datum[8]=="y":
                    number_yt+=1
                elif datum[8]=="O":
                    number_ol+=1
                elif datum[8]=="C":
                    number_c+=1
                else:
                    number_local+=1
                
            if datum[5]!=datum[6] or datum[8]!=datum[9] or datum[10]!=datum[11]:
                
                MainApp.save_now(datum)
                y = list(datum)
                y[6]=y[5]
                y[9]=y[8]
                y[11]=y[10]
                MainApp.data[bilang]=tuple(y)

        number_total= number_local+number_zoom+number_yt+number_ol+number_c
        report_text=""

        if MainApp.event_title!=None:
            report_text=MainApp.event_title
        else:
            report_text='<no title yet>'


        report_text=report_text+"\n"+MainApp.event_date.strftime("%B %d, %Y")

        report_text=report_text+"\nLOCAL: PANGHULO\n"
        
        
        report_text=report_text+"\nLokal: "+str(number_local)
        report_text=report_text+"\nZoom:  "+str(number_zoom)
        report_text=report_text+"\nYT: "+str(number_yt)
        report_text=report_text+"\nDumalo sa ibang lokal: "+str(number_ol)
        report_text=report_text+"\nChapel: "+str(number_c)
        report_text=report_text+"\nTotal: "+str(number_total)
        return report_text
        
    def on_leave(self, *args):
        global text_report
        text_report.text=""
        return super().on_leave(*args)

    def on_enter(self, *args):
        global text_report
        global text_search_group
        self.search_group=text_search_group.text.upper().strip()
        if len(self.search_group)==0:
            text_report.text=self.report_total_all()
        else:
            text_report.text=self.report_per_group()
        clipboard.copy(text_report.text) 
        return super().on_enter(*args)
    
    
class MainAppMember:
    def __init__(self, datum,bilang):
        self.bilang=bilang
        self.datum=datum

def my_string_2_date(str_date):  #0123-56-78
    year=int(str_date[0:4])
    month=int(str_date[5:7])
    day=int(str_date[8:10])
    return (year,month,day)

def make_setup(cur):
    query = "SELECT setup.event_date,batch_mins,event_title,foot_note FROM setup JOIN events ON setup.event_date=events.event_date"
    cur.execute(query)
    data = cur.fetchone()

    #event_date=data[0]
    (year,month,day)=my_string_2_date(data[0])
    event_date = datetime.datetime(year=year,month=month,day=day)
    batch_mins = data[1]
    event_title= data[2]
    foot_note  = data[3]
    return (event_date,batch_mins,event_title,foot_note)

class MainApp(App):
    con = sqlite3.connect("pms_db")
    cur = con.cursor()


    global mga_miembro
    global linya_max
    global pahina_no
    global miembro_rows
    global filter_text_row



    event_date,batch_mins,event_title,foot_note = make_setup(cur)
    # query = "SELECT setup.event_date,batch_mins FROM setup JOIN events ON setup.event_date=events.event_date"
    # cur.execute(query)
    # data = cur.fetchone()

    # #event_date=data[0]
    # (year,month,day)=my_string_2_date(data[0])
    # event_date = datetime.datetime(year=year,month=month,day=day)
    # batch_mins = data[1]
    # event_date=datetime.date(year=year,month=month,day=day)

    # time_change = datetime.timedelta(minutes=1020) 
    # new_time = date_and_time + time_change 
    #                            0          1         2           3          4       5       6          7      8      9         10         11  12
    query = "SELECT members.key_id,first_name,last_code,group_code,member_type,checked,checked,event_date,a_type,a_type,batch_mins,batch_mins,sex FROM members LEFT OUTER JOIN attendance ON members.key_id=attendance.key_id AND attendance.event_date=? ORDER BY substr('0000000000' || group_code, -10, 10),first_name"
    cur.execute(query,(str(event_date)[0:10],))
    data = cur.fetchall()

    mga_miembro = []


    linya_max = 10
    pahina_no = 1
    miembro_rows = []
    filter_mode = "wo"
        
    for bilang,datum in enumerate(data):
        mga_miembro.append(MainAppMember(datum,bilang))



    def filtering(variable):
        global filter_text_row
        global text_search_name
        global text_search_group
        search_name=text_search_name.text.upper().strip()
        search_group=text_search_group.text.upper().strip()
        name=variable[1].upper()+variable[2].upper().strip()
        group=variable[3].upper().strip()
        checked=variable[5]
        if ((search_name=="" or (search_name in name)) 
            and (search_group=="" or search_group==group)
            and (MainApp.filter_mode=="all" or checked==None)):
            return True
        else:
            return False

    def filter_now(filter_mode):
        global pahina_no
        global mga_miembro
        MainApp.filter_mode=filter_mode
        mga_miembro = []

        for bilang,datum in enumerate(MainApp.data):
            if datum[5]!=datum[6] or datum[8]!=datum[9] or datum[10]!=datum[11]:
                MainApp.save_now(datum)

                y = list(datum)
                y[6]=y[5]
                y[9]=y[8]
                y[11]=y[10]

                # self.member.datum = tuple(y)
                # miembro_rows[self.numero].member=self.member
                MainApp.data[bilang]=tuple(y)

            if MainApp.filtering(datum):
                mga_miembro.append(MainAppMember(datum,bilang))

        pahina_no=1
        PagerRow.act_paging(pager_row)

    def save_now(datum):
        
        sql = "SELECT key_id,event_date,checked FROM attendance WHERE event_date=? AND key_id=?"
        MainApp.cur.execute(sql, (str(MainApp.event_date)[0:10],datum[0]))
        data_one = MainApp.cur.fetchone()
        # print(data_one)
        if data_one!=None:
            sql = 'UPDATE attendance SET checked=?,a_type=?,batch_mins=?  WHERE key_id = ? AND event_date = ?'
            MainApp.cur.execute(sql, (datum[5],datum[8],datum[10],datum[0],data_one[1]))
            MainApp.con.commit()
        else:
            sql = 'INSERT INTO attendance VALUES(?,?,?,?,?)'
            MainApp.cur.execute(sql, (datum[0],str(MainApp.event_date)[0:10],datum[5],datum[8],datum[10]))
            MainApp.con.commit()




    def build(self):
        # for bilang,datum in enumerate(self.data):
        #     mga_miembro.append(MainAppMember(datum,bilang))
        return MyMainWindow()  # kv

if __name__ == "__main__":
    MainApp().run()




