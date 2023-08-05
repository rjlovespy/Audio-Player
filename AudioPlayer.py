from tkinter import *
from tkinter.filedialog import askopenfilename, askopenfiles
import tkinter.messagebox as tmsg
from mutagen.mp3 import MP3
import pygame, mutagen, os, time


def addSingleAudio():
    audio = askopenfilename(filetypes=[("Audio File","*.mp3")])
    entries.append(audio)
    playlist.insert(END, os.path.basename(audio))
    # The following bloack prevents appearing single audio twice in the playlist
    if entries.count(audio) >= 2:
        del entries[-1]
        playlist.delete(END)
        
def addMultipleAudios():
    audios = askopenfiles(filetypes=[("Audio Files","*.mp3")])
    last_index = len(entries)
    for obj in audios:
        entries.append(obj.name)
        playlist.insert(END, os.path.basename(obj.name))
    # The following block prevents appearing mutliple audios twice in the playlist  
    naef, red_entries = [], [] 
    for i in range(last_index, len(entries)):
        naef.append(entries.count(entries[i]))
        if naef[-1] >= 2:
            red_entries.append(i)
    if len(red_entries) >= 1:   
        decrement = 0        
        for i in red_entries:
            del entries[i+decrement]
            playlist.delete(i+decrement)
            decrement -= 1
                    
def removeSingleAudio():
    try:
        if pygame.mixer.music.get_busy():
            stopAudio()
        playlist.delete(ACTIVE)
        index = playlist.index(ACTIVE)
        del entries[index]
    # This IndexError exception block handles the attempt to remove an audio without selection
    except IndexError:
        tmsg.showinfo(title="Warning!!!", message="Select an audio")

def removeAllAudios():
    if pygame.mixer.music.get_busy():
        stopAudio()
    playlist.delete(0, END)
    del entries[:]

def addInstructions():
    file = open("E:\\GUI Development\\News\\audio_player_instructions.txt","r")
    tmsg.showinfo(title="Instructions", message=file.read())
    
def addAbout():
    file = open("E:\\GUI Development\\News\\audio_player_about.txt","r")
    tmsg.showinfo(title="About", message=file.read())

def addRating():
    def cancelRating():
        F.destroy()
    def submitRating():
        # Appending the user's rating via creating a text file
        file = open("E:\\GUI Development\\News\\audio_player_rating.txt", "a+")
        file.write(str(rating.get()) + "\n")
        F.destroy() 
    F = Frame(root, bg="#BDBDB7", highlightbackground="white", highlightthickness=2)
    F.place(x=200, y=200, width=400, height=200)
    rating = Scale(F, from_=0, to=10, orient=HORIZONTAL, length=350, activebackground="deepskyblue", troughcolor="PeachPuff2", background="#BDBDB7")
    rating.pack(pady=25, padx=25)
    Button(F, text="CANCEL", command=cancelRating, width=12, bg="red2", font=("Lucida", 12, "bold"), activebackground="deepskyblue", bd=5, relief=SUNKEN).pack(side=LEFT, padx=25)
    Button(F, text="SUBMIT", command=submitRating, width=12, bg="lime", font=("Lucida", 12, "bold"), activebackground="deepskyblue", bd=5, relief=SUNKEN).pack(side=RIGHT, padx=25)
    
def pauseAudio():
    global t2
    pygame.mixer.music.pause()
    t2 = time.perf_counter()

def playAudio():
    try:
        global t1, desired_position, AUDIO
        selected_index = playlist.curselection()
        selected_audio = entries[selected_index[0]]
        AUDIO = MP3(selected_audio)
        del desired_position[:]
        desired_position = [0]
        pygame.mixer.music.load(selected_audio)
        pygame.mixer.music.play()
        t1 = time.perf_counter()
        updateCurrentTime()
    # This IndexError exception block handles the attempt to play an audio without selection
    except IndexError:
        tmsg.showinfo(title="Warning!!!", message="Select an audio")
    # This mutagen.mp3.HeaderNotFoundError exception block removes the audio files whose names contain punctuation marks or special characters
    except mutagen.mp3.HeaderNotFoundError:
        removeSingleAudio()
        tmsg.showinfo(title="Warning!!!", message="Invalid file name")
    # This pygame.error exception block removes the corrupted audio files
    except pygame.error:
        removeSingleAudio()
        tmsg.showinfo(title="Warning!!!", message="Corrupted file")

def stopAudio():
    # Stopping an audio via setting the desired position equal to its entire length
    desired_position[-1] = AUDIO.info.length
    
def unpauseAudio():
    global t3, is_unpaused
    pygame.mixer.music.unpause()
    t3 = time.perf_counter()
    is_unpaused = True
            
def playPreviousAudio():
    try:
        global t1, desired_position, AUDIO
        selected_index = playlist.curselection()
        # This if block prevents playing a previous audio if the currently selected audio is the first audio in the playlist or if mutltiple audios are not added in the playlist
        if selected_index[0] == 0:
            tmsg.showinfo(title="Warning!!!", message="This is the first audio in the playlist")
            return None
        playlist.selection_clear(0, END)
        playlist.activate(selected_index[0]-1)
        playlist.selection_set(selected_index[0]-1)
        selected_audio = entries[selected_index[0]-1]
        AUDIO = MP3(selected_audio)
        del desired_position[:]
        desired_position = [0]
        pygame.mixer.music.load(selected_audio)
        pygame.mixer.music.play()
        t1 = time.perf_counter()
        updateCurrentTime()
    # This IndexError exception block prevents playing a previous audio if no audio is selected yet 
    except IndexError:
        tmsg.showinfo(title="Warning!!!", message="Add multiple audios and select any one except the first audio")
    # This mutagen.mp3.HeaderNotFoundError exception block removes the audio files whose names contain punctuation marks or special characters
    except mutagen.mp3.HeaderNotFoundError:
        stopAudio()
        playlist.delete(selected_index[0] -1) 
        del entries[selected_index[0]-1]  
        tmsg.showinfo(title="Warning!!!", message="Invalid file name")
    # This pygame.error exception block removes the corrupted audio files
    except pygame.error:
        stopAudio()
        playlist.delete(selected_index[0] -1) 
        del entries[selected_index[0]-1]  
        tmsg.showinfo(title="Warning!!!", message="Corrupted file")
        
def skipBackwardAudio():
    if pygame.mixer.music.get_busy():
        # This if block handles backward audio skip when audio is played, paused, unpaused, and skipped backward
        global t1, desired_position, is_unpaused
        if is_unpaused:
            t4 = time.perf_counter()
            # (t2 - t1) is the time elpased between play and pause
            # (t3 - t2) is the time elapsed between pause and unpause
            # (t4 - t3) is the time elapsed between unpause and backward skip
            new_from = (t2 - t1) + (t4 - t3) + desired_position[-1] - 30
            desired_position.append(new_from)
            pygame.mixer.music.play(start=new_from)
            t1 = t4
            is_unpaused = False
        # This else block handles backward audio skip when audio is played and skipped backward
        else:
            t4 = time.perf_counter()
            new_from = (t4 - t1) + desired_position[-1] - 30
            desired_position.append(new_from)
            pygame.mixer.music.play(start=new_from)
            t1 = t4
    # This else block handles backward audio skip when audio is played, paused, and skipped backward or when no audio is selected or when audio has gone beyond its initial position  or when audio has gone beyond or at its final position 
    else:
        tmsg.showinfo(title="Warning!!!", message="To skip, audio must be on")
        
def skipForwardAudio():
    if pygame.mixer.music.get_busy():
        # This if block handles forward audio skip when audio is played, paused, unpaused, and skipped forward
        global t1, desired_position, is_unpaused
        if is_unpaused:
            t4 = time.perf_counter()
            # (t2 - t1) is the time elpased between play and pause
            # (t3 - t2) is the time elapsed between pause and unpause
            # (t4 - t3) is the time elapsed between unpause and forward skip
            new_from = (t2 - t1) + (t4 - t3) + desired_position[-1] + 30
            desired_position.append(new_from)
            pygame.mixer.music.play(start=new_from)
            t1 = t4
            is_unpaused = False
        # This else block handles forward audio skip when audio is played and skipped forward
        else:
            t4 = time.perf_counter()
            new_from = (t4 - t1) + desired_position[-1] + 30
            desired_position.append(new_from)
            pygame.mixer.music.play(start=new_from)
            t1 = t4
    # This else block handles forward audio skip when audio is played, paused, and skipped forward or when no audio is selected or when audio has gone beyond its initial position or when audio has gone beyond or at its final position 
    else:
        tmsg.showinfo(title="Warning!!!", message="To skip, audio must be on")
       
def playNextAudio():
    try:
        global t1, desired_position, AUDIO
        selected_index = playlist.curselection()
        # This if block prevents playing a next audio if the currently selected audio is the last audio in the playlist or if mutltiple audios are not added in the playlist
        if selected_index[0] == len(entries)-1:
            tmsg.showinfo(title="Warning!!!", message="This is the last audio in the playlist")
            return None
        playlist.selection_clear(0, END)
        playlist.activate(selected_index[0]+1)
        playlist.selection_set(selected_index[0]+1)
        selected_audio = entries[selected_index[0]+1]
        AUDIO = MP3(selected_audio)
        del desired_position[:]
        desired_position = [0]
        pygame.mixer.music.load(selected_audio)
        pygame.mixer.music.play()
        t1 = time.perf_counter()
        updateCurrentTime()
    # This IndexError exception block prevents playing a next audio if no audio is selected yet
    except IndexError:
        tmsg.showinfo(title="Warning!!!", message="Add multiple audios and select any one except the last audio")
    # This mutagen.mp3.HeaderNotFoundError exception block removes the audio files whose names contain punctuation marks or special characters
    except mutagen.mp3.HeaderNotFoundError:
        stopAudio()
        playlist.delete(selected_index[0] +1) 
        del entries[selected_index[0]+1]  
        tmsg.showinfo(title="Warning!!!", message="Invalid file name")
    # This pygame.error exception block removes the corrupted audio files
    except pygame.error:
        stopAudio()
        playlist.delete(selected_index[0] +1) 
        del entries[selected_index[0]+1]
        tmsg.showinfo(title="Warning!!!", message="Corrupted file")
        
def updateCurrentTime():
    playing_time = pygame.mixer.music.get_pos() / 1000
    current_position = playing_time + desired_position[-1]
    if int(current_position) >= int(AUDIO.info.length):
        formatted_current_position = time.strftime("%M:%S", time.gmtime(AUDIO.info.length))
        current_time["text"] = f"Current time is {formatted_current_position}"
        pygame.mixer.quit()  
        pygame.mixer.init()
    elif int(current_position) < 0:
        current_time["text"] = "Current time is 00:00"
        pygame.mixer.quit()  
        pygame.mixer.init()
    else:
        formatted_current_position = time.strftime("%M:%S", time.gmtime(current_position))
        current_time["text"] = f"Current time is {formatted_current_position}"
        current_time.after(1000, updateCurrentTime)

def updateSelection():
    try: 
        selected_audio_tuple = playlist.curselection()
        selected_audio_index = selected_audio_tuple[0] + 1
        selection["text"] = f"Selected Audio: {selected_audio_index} out of {len(entries)}"
        selection.after(100, updateSelection)
    except IndexError:
        selection["text"] = f"Selected Audio: None out of {len(entries)}"
        selection.after(100, updateSelection)
        
def updateEndTime():
    try:
        AUDIO_LENGTH = time.strftime("%M:%S", time.gmtime(AUDIO.info.length))
        end_time["text"] = f"End time is {AUDIO_LENGTH}"
        end_time.after(100, updateEndTime)
    except NameError:
        end_time["text"] = "End time is none"
        end_time.after(100, updateEndTime)
        
            
# Basic setup of a window creation             
root = Tk()
root.geometry("800x750")
root.config(bg="#BDBDB7")
root.title("Audio Player [Version 0.1]")
root.resizable(False, True)
root.iconbitmap("audio_player.ico")
# logo = PhotoImage(file="E:\\GUI Development\\News\\audio_player.png")
# root.iconphoto(False, logo)
pygame.mixer.init()
entries, desired_position, t1, is_unpaused = [], [0], None, False

# Creating Dropdown Menu
menubar = Menu(root)
addMenu = Menu(menubar, tearoff=0)
addMenu.add_command(label="Add Single Audio", command=addSingleAudio, font=("Lucida", 12, "bold"), background="lavender", activeforeground="black", activebackground="gold")
addMenu.add_separator()
addMenu.add_command(label="Add Multiple Audios", command=addMultipleAudios, font=("Lucida", 12, "bold"), background="lavender", activeforeground="black", activebackground="gold")
menubar.add_cascade(label="Add", menu=addMenu)
removeMenu = Menu(menubar, tearoff=0)
removeMenu.add_command(label="Remove Single Audio", command=removeSingleAudio, font=("Lucida", 12, "bold"), background="lavender", activeforeground="black", activebackground="gold")
removeMenu.add_separator()
removeMenu.add_command(label="Remove All Audios", command=removeAllAudios, font=("Lucida", 12, "bold"), background="lavender", activeforeground="black", activebackground="gold")
menubar.add_cascade(label="Remove", menu=removeMenu)
helpMenu = Menu(menubar, tearoff=0)
helpMenu.add_command(label="Instructions", command=addInstructions, font=("Lucida", 12, "bold"), background="lavender", activeforeground="black", activebackground="gold")
helpMenu.add_separator()
helpMenu.add_command(label="About", command=addAbout, font=("Lucida", 12, "bold"), background="lavender", activeforeground="black", activebackground="gold")
helpMenu.add_separator()
helpMenu.add_command(label="Rate me", command=addRating, font=("Lucida", 12, "bold"), background="lavender", activeforeground="black", activebackground="gold")
menubar.add_cascade(label="Help", menu=helpMenu)
root.config(menu=menubar)

# Dividing window into three frames
f1 = Frame(root)
f1.pack(pady=20, expand=True)
f2 = Frame(root, bg="#BDBDB7")
f2.pack(expand=True)
f3 = Frame(root)
f3.pack(anchor=S, fill=X, expand=True)

# Placing a listboc in one frame
playlist = Listbox(f1, width=54, height=15, font=("Comic Sans MS", 14, "bold"), bg="lavender", justify=LEFT, selectforeground="black", selectbackground="gold", bd=5, relief=FLAT)
playlist.pack(side=LEFT)
scrollpipe = Scrollbar(f1, jump=True)
scrollpipe.pack(side=RIGHT, fill=Y)
scrollpipe.config(command=playlist.yview)
playlist.config(yscrollcommand=scrollpipe.set)

# Placing buttons in the second frame
image1 = PhotoImage(file="E:\\GUI Development\\News\\pause_button.png")
image2 = PhotoImage(file="E:\\GUI Development\\News\\play_button.png")
image3 = PhotoImage(file="E:\\GUI Development\\News\\stop_button.png")
image4 = PhotoImage(file="E:\\GUI Development\\News\\unpause_button.png")
image5 = PhotoImage(file="E:\\GUI Development\\News\\previous_button.png")
image6 = PhotoImage(file="E:\\GUI Development\\News\\skip_backward_button.png")
image7 = PhotoImage(file="E:\\GUI Development\\News\\skip_forward_button.png")
image8 = PhotoImage(file="E:\\GUI Development\\News\\next_button.png")
Button(f2, image=image1, bd=5, relief=SUNKEN, activebackground="crimson", command=pauseAudio).grid(row=0, column=0, padx=10)
Button(f2, image=image2, bd=5, relief=SUNKEN, activebackground="crimson", command=playAudio).grid(row=0, column=1)
Button(f2, image=image3, bd=5, relief=SUNKEN, activebackground="crimson", command=stopAudio).grid(row=0, column=2, padx=10)
Button(f2, image=image4, bd=5, relief=SUNKEN, activebackground="crimson", command=unpauseAudio).grid(row=0, column=3)
Button(f2, image=image5, bd=5, relief=SUNKEN, activebackground="crimson", command=playPreviousAudio).grid(row=1, column=0, padx=10, pady=5)
Button(f2, image=image6, bd=5, relief=SUNKEN, activebackground="crimson", command=skipBackwardAudio).grid(row=1, column=1)
Button(f2, image=image7, bd=5, relief=SUNKEN, activebackground="crimson", command=skipForwardAudio).grid(row=1, column=2, padx=10)
Button(f2, image=image8, bd=5, relief=SUNKEN, activebackground="crimson", command=playNextAudio).grid(row=1, column=3)

# Placing statusbar in the third frame
current_time = Label(f3, text="Current time is 00:00", font=("Lucida",14,"bold"))
current_time.pack(side=LEFT, ipadx=10, ipady=5)
selection = Label(f3, text="Selected Audio: None out of 0", font=("Lucida",14,"bold"))
selection.pack(side=LEFT, ipadx=60, ipady=5)
end_time = Label(f3, text="End time is none", font=("Lucida",14,"bold"))
end_time.pack(side=RIGHT, ipadx=10, ipady=5)

# Updating end_time and selection status every 100 milliseconds
updateSelection()
updateEndTime()
root.mainloop()