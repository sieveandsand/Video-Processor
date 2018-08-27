from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import *
import os, datetime
from threading import Thread


class App:
    def __init__(self, master):
        self.master = master
        master.title("Video Processing Tool")
        master.geometry('500x200')

        self.button1 = Button(master, text="Select Input Video(s)", command=lambda: App.clicked(self, master))
        self.button1.grid(column=0, row=0)

        self.locations = ()  # video file path
        self.video_count = -1  # number of videos imported by the user
        self.entries = []
        self.label_list = []
        self.prompt_check = False

        self.chk_state = BooleanVar()
        self.chk_state.set(True)
        self.chk = Checkbutton(master, text="Add Time Stamp", var=self.chk_state)
        self.chk.grid(column=0, row=1)

        self.chk_state_2 = BooleanVar()
        self.chk_state_2.set(False)
        self.chk_time = Checkbutton(master, text="Select Time Segment", var=self.chk_state_2)
        self.chk_time.grid(column=0, row=2)

        self.button2 = Button(master, text="Output Frames", command=self.output)
        self.button2.grid(column=0, row=3)

        self.prompt_lbl = Label(master)

        self.start_lbl = Label(master, text="Start Time")
        self.end_lbl = Label(master, text="Duration")
        self.note_lbl = Label(master, text="(Enter Seconds\nin Positive Integers)")

        # disables output button if no video is selected
        if self.video_count <= 0:
            self.button2.config(state=DISABLED)

    def clicked(self, master):
        """checks if the button is clicked, if so, opens file dialog"""
        self.locations = filedialog.askopenfilenames(filetypes=(("video files", "*.mov *.mp4 *.avi *.flv *.wmv"),
                                                                ("all files", "*.*")))
        self.video_count = len(self.locations)

        # enables output button if video(s) is selected
        # disables output button if no video is selected
        if self.video_count > 0:
            self.button2.config(state=NORMAL)
        else:
            self.button2.config(state=DISABLED)

        # extracts folder names from file path & makes folders
        for location in self.locations:
            name = location[:-4]
            # checks if current folder already exits
            if not os.path.isdir(name):
                os.mkdir(name)

        # checks if time selection is checked, if so makes entry boxes and labels
        if self.chk_state_2.get():
            App.time_selection(self, master)
            self.prompt_lbl.grid_forget()
        else:
            App.forget_time_selection(self)
            self.prompt_lbl.config(text=str(self.video_count) + " video(s) selected")
            self.prompt_lbl.grid(column=3, row=0)

    def output(self):
        """outputs frames"""
        if self.chk_state_2.get():
            App.check_input(self)

        stamp_command = "-vf \"drawtext=fontfile=/WINDOWS/fonts/Arial.ttf: text=\'%{pts\\:flt}\': " \
                        "x=(w-tw)/2: y=h-(2*lh): fontcolor=white: box=1: boxcolor=0x00000000@1\""
        cmd = ""

        process_count = 1

        for location in self.locations:
            if not self.chk_state.get() and not self.chk_state_2.get():
                cmd = "ffmpeg -i \"" + location + "\" " + " \"" + location[:-4] + "/image%03d.png\""
            elif self.chk_state.get() and not self.chk_state_2.get():
                cmd = "ffmpeg -i \"" + location + "\" " + stamp_command + " \"" + location[:-4] + "/image%03d.png\""
            else:
                tracker = 0
                start = ""
                duration = ""
                while tracker < (self.video_count * 2):
                    start = str(datetime.timedelta(seconds=int(self.entries[tracker].get())))
                    duration = str(datetime.timedelta(seconds=int(self.entries[tracker + 1].get())))
                    tracker += 2

                if self.chk_state.get():
                    cmd = "ffmpeg -ss " + start + " -i \"" + location + "\" -t " + duration + " " \
                          + stamp_command + " \"" + location[:-4] + "/image%03d.png\""
                else:
                    cmd = "ffmpeg -ss " + start + " -i \"" + location + "\" -t " + duration + " " \
                          + " \"" + location[:-4] + "/image%03d.png\""

            thread = Thread(group=None, target=lambda: os.system(cmd))
            thread.run()
            if not thread.is_alive():
                messagebox.showinfo("Info", "Process " + str(process_count) + " Out Of "
                                    + str(self.video_count) + " Finished")

            process_count += 1

    def time_selection(self, master):
        """generates multiple entry boxes and labels for specifying time segment"""
        row_number = 1
        current_val = 0

        # clears data stored from previous operation
        for label in self.label_list:
            label.grid_forget()
        for field in self.entries:
            field.grid_forget()
        self.label_list.clear()
        self.entries.clear()

        if self.video_count > 0:
            self.start_lbl.grid(column=2, row=0)
            self.end_lbl.grid(column=3, row=0)
            self.note_lbl.grid(column=4, row=0)

        while current_val < self.video_count:
            video_lbl = Label(master, text="Video " + str(current_val + 1))  # adds video identification label
            video_lbl.grid(column=1, row=row_number)
            self.label_list.append(video_lbl)

            field1 = Entry(master, width=10)  # field1 is for start time
            field1.grid(column=2, row=row_number)
            self.entries.append(field1)

            field2 = Entry(master, width=10)  # field2 is for end time
            field2.grid(column=3, row=row_number)
            self.entries.append(field2)

            row_number = row_number + 1
            current_val = current_val + 1

    def forget_time_selection(self):
        # forgets entry fields
        for field in self.entries:
            field.grid_forget()

        # forgets the video identification label
        for label in self.label_list:
            label.grid_forget()

        self.start_lbl.grid_forget()
        self.end_lbl.grid_forget()
        self.note_lbl.grid_forget()

    def check_input(self):
        for field in self.entries:
            try:
                int(field.get())
            except ValueError:
                messagebox.showinfo("Warning", "Please Enter a Positive Integer")
                raise


root = Tk()
gui = App(root)
root.mainloop()
